from datetime import datetime

import asyncpgsa
import pytz
from sqlalchemy.dialects.postgresql import insert

from external_offers import pg
from external_offers.entities.parsed_offers import ParsedOffer
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


async def get_parsed_offer(*, parsed_offer_id: str) -> None:
    return
