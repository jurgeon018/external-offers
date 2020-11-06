import json
from datetime import datetime
from typing import Optional

import asyncpgsa
import pytz
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import select

from external_offers import pg
from external_offers.entities.parsed_offers import ParsedObjectModel, ParsedOffer
from external_offers.mappers.parsed_object_model import parsed_object_model_mapper
from external_offers.mappers.parsed_offers import parsed_offer_mapper
from external_offers.repositories.postgresql import tables


async def save_parsed_offer(*, parsed_offer: ParsedOffer) -> None:
    insert_query = insert(tables.parsed_offers_table)

    now = datetime.now(tz=pytz.UTC)
    values = parsed_offer_mapper.map_to(parsed_offer)
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
                'is_calltracking': insert_query.excluded.is_calltracking,
                'updated_at': insert_query.excluded.updated_at,
                'timestamp': insert_query.excluded.timestamp,
            }
        )
    )

    await pg.get().execute(query, *params)


async def get_parsed_offer_object_model_by_offer_for_call_id(*, offer_id: str) -> Optional[ParsedObjectModel]:
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
