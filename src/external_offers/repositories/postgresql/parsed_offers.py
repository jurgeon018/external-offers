from datetime import datetime
from typing import AsyncGenerator, List, Optional

import asyncpgsa
import pytz
from cian_json import json
from simple_settings import settings
from sqlalchemy import JSON, func
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, delete, not_, select, update

from external_offers import pg
from external_offers.entities.parsed_offers import (
    ParsedObjectModel,
    ParsedOffer,
    ParsedOfferForCreation,
    ParsedOfferMessage,
)
from external_offers.mappers.parsed_object_model import parsed_object_model_mapper
from external_offers.mappers.parsed_offers import (
    parsed_offer_for_creation_mapper,
    parsed_offer_mapper,
    parsed_offer_message_mapper,
)
from external_offers.repositories.postgresql import tables


async def save_parsed_offer(*, parsed_offer: ParsedOfferMessage) -> None:
    insert_query = insert(tables.parsed_offers)

    now = datetime.now(tz=pytz.UTC)
    values = parsed_offer_message_mapper.map_to(parsed_offer)
    values['created_at'] = now
    values['updated_at'] = now

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        ).on_conflict_do_update(
            index_elements=[tables.parsed_offers.c.source_object_id],
            where=(
                    tables.parsed_offers.c.timestamp <= parsed_offer.timestamp
            ),
            set_={
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
    *,
    last_sync_date: Optional[datetime]
) -> Optional[List[ParsedOfferForCreation]]:
    po = tables.parsed_offers.alias()
    options = [
        po.c.source_object_model['phones'] != JSON.NULL,
        po.c.source_object_model['phones'] != [''],
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
        select([
            po,
        ])
        .where(
            and_(*options)
        )
        .limit(settings.OFFER_TASK_CREATION_OFFER_FETCH_LIMIT)
        .cte('selected_non_synced_offers_cte')
    )

    fetch_offers_query, fetch_offers_params = asyncpgsa.compile_query(
        update(tables.parsed_offers)
        .where(
            tables.parsed_offers.c.id == selected_non_synced_offers_cte.c.id
        )
        .values(synced=True)
        .returning(
            tables.parsed_offers.c.id,
            tables.parsed_offers.c.source_user_id,
            tables.parsed_offers.c.timestamp,
            tables.parsed_offers.c.created_at,
            tables.parsed_offers.c.user_segment,
            tables.parsed_offers.c.source_object_model['phones'].label('phones'),
            tables.parsed_offers.c.source_object_model['contact'].label('contact'),
            tables.parsed_offers.c.source_object_model['category'].label('category')
        )
    )
    rows = await pg.get().fetch(fetch_offers_query, *fetch_offers_params)

    return [parsed_offer_for_creation_mapper.map_from(row) for row in rows]


async def get_parsed_offer_object_model_by_offer_id(*, offer_id: str) -> Optional[ParsedObjectModel]:
    po = tables.parsed_offers.alias()
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


async def get_parsed_offer_by_offer_id(*, offer_id: str) -> Optional[ParsedOffer]:
    po = tables.parsed_offers.alias()
    ofc = tables.offers_for_call.alias()

    query, params = asyncpgsa.compile_query(
        select([po])
        .select_from(
            po.join(
                ofc,
                po.c.id == ofc.c.parsed_id
            )
        )
        .where(ofc.c.id == offer_id)
    )

    row = await pg.get().fetchrow(query, *params)

    return parsed_offer_mapper.map_from(row) if row else None


async def get_lastest_event_timestamp() -> Optional[datetime]:
    po = tables.parsed_offers.alias()
    query, params = asyncpgsa.compile_query(
        select([
            func.max(po.c.timestamp)
        ])
        .limit(1)
    )

    return await pg.get().fetchval(query, *params)


async def get_latest_updated_at() -> Optional[datetime]:
    po = tables.parsed_offers.alias()
    query, params = asyncpgsa.compile_query(
        select([
            func.max(po.c.updated_at)
        ])
        .limit(1)
    )

    return await pg.get().fetchval(query, *params)


async def delete_outdated_parsed_offers(
    *,
    updated_at_border: datetime
) -> List[str]:
    po = tables.parsed_offers.alias()

    sql = (
        delete(
            po
        ).where(
            po.c.id.in_(
                select(
                    [
                        po.c.id
                    ]
                ).where(
                    po.c.updated_at < updated_at_border
                ).limit(
                    settings.CLEAR_OUTDATED_PARSED_OFFERS_CHUNK
                )
            )
        ).returning(
            po.c.source_object_id
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    rows = await pg.get().fetch(query, *params)
    return [
        row['source_object_id'] for row in rows
    ]


async def iterate_over_parsed_offers_sorted(
    *,
    prefetch=settings.DEFAULT_PREFETCH,
) -> AsyncGenerator[ParsedOffer, None]:
    po = tables.parsed_offers.alias()
    query, params = asyncpgsa.compile_query(
        select(
            [po]
        ).order_by(
            po.c.created_at.asc(),
            po.c.id.asc()
        )
    )
    cursor = await pg.get().cursor(
        query,
        *params,
        prefetch=prefetch
    )
    async for row in cursor:
        yield parsed_offer_mapper.map_from(row)
