from datetime import datetime
from typing import List, Optional

import asyncpgsa
import pytz
from cian_json import json
from simple_settings import settings
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, not_, select, update

from external_offers import pg
from external_offers.entities.parsed_offers import ParsedObjectModel, ParsedOffer, ParsedOfferMessage
from external_offers.mappers.parsed_object_model import parsed_object_model_mapper
from external_offers.mappers.parsed_offers import parsed_offer_mapper, parsed_offer_message_mapper
from external_offers.repositories.postgresql import tables


async def save_parsed_offer(*, parsed_offer: ParsedOfferMessage) -> None:
    insert_query = insert(tables.parsed_offers_table)

    now = datetime.now(tz=pytz.UTC)
    values = parsed_offer_message_mapper.map_to(parsed_offer)
    values['created_at'] = now
    values['updated_at'] = now

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        ).on_conflict_do_update(
            index_elements=[tables.parsed_offers_table.c.id],
            where=(
                    tables.parsed_offers_table.c.timestamp < parsed_offer.timestamp
            ),
            set_={
                'id': insert_query.excluded.id,
                'user_segment': insert_query.excluded.user_segment,
                'source_object_id': insert_query.excluded.source_object_id,
                'source_user_id': insert_query.excluded.source_user_id,
                'source_object_model': insert_query.excluded.source_object_model,
                'synced': False,
                'is_calltracking': insert_query.excluded.is_calltracking,
                'updated_at': insert_query.excluded.updated_at,
                'timestamp': insert_query.excluded.timestamp,
            }
        )
    )

    await pg.get().execute(query, *params)


async def set_synced_and_fetch_parsed_offers_chunk(
    *, last_sync_date: Optional[datetime]
) -> Optional[List[ParsedOffer]]:
    po = tables.parsed_offers_table.alias()
    options = [
        po.c.source_object_model['phones'] != JSON.NULL,
        not_(po.c.is_calltracking),
        not_(po.c.synced),
    ]

    if settings.OFFER_TASK_CREATION_CATEGORIES:
        options.append(po.c.source_object_model['category'].as_string().in_(settings.OFFER_TASK_CREATION_CATEGORIES))

    if settings.OFFER_TASK_CREATION_SEGMENTS:
        options.append(po.c.user_segment.in_(settings.OFFER_TASK_CREATION_SEGMENTS))

    if settings.OFFER_TASK_CREATION_REGIONS:
        options.append(po.c.source_object_model['region'].as_integer().in_(settings.OFFER_TASK_CREATION_REGIONS))

    if last_sync_date:
        options.append(po.c.timestamp > last_sync_date)

    selected_non_synced_offers_cte = (
        select(
            [po]
        )
        .where(
            and_(*options)
        )
        .limit(
            settings.OFFER_TASK_CREATION_FETCH_LIMIT
        )
        .cte('selected_non_synced_offers_cte')
    )

    query, params = asyncpgsa.compile_query(
        update(tables.parsed_offers_table)
        .where(
            tables.parsed_offers_table.c.id.in_(
                select(
                    [selected_non_synced_offers_cte.c.id]
                )
            )
        )
        .values(synced=True)
        .returning(tables.parsed_offers_table)
    )

    rows = await pg.get().fetch(query, *params)
    return [parsed_offer_mapper.map_from(row) for row in rows]


async def get_parsed_offer_object_model_by_offer_id(*, offer_id: str) -> Optional[ParsedObjectModel]:
    po = tables.parsed_offers_table.alias()
    ofc = tables.offers_for_call.alias()

    query, params = asyncpgsa.compile_query(
        select([po.c.source_object_model])
        .select_from(
            po.join(
                ofc,
                po.c.id == ofc.c.parsed_id
            )
        )
        .where(ofc.c.id == offer_id)
    )

    row = await pg.get().fetchrow(query, *params)

    return parsed_object_model_mapper.map_from(json.loads(row['source_object_model'])) if row else None
