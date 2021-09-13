from datetime import datetime, timedelta
from typing import AsyncGenerator, List, Optional

import asyncpgsa
import pytz
from cian_core.runtime_settings import runtime_settings as settings
from cian_json import json
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, delete, func, not_, select, update, or_
from sqlalchemy.sql.selectable import Alias
from sqlalchemy.sql.expression import false, true

from external_offers import pg
from external_offers.entities.parsed_offers import (
    ParsedObjectModel,
    ParsedOffer,
    ParsedOfferForCreation,
    ParsedOfferMessage,
)
from external_offers.enums.object_model import Category
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
                'external_offer_type': insert_query.excluded.external_offer_type,
            }
        )
    )

    await pg.get().execute(query, *params)


async def save_test_parsed_offer(
    *,
    parsed_offer: ParsedOfferMessage
) -> None:
    insert_query = insert(tables.parsed_offers)

    values = parsed_offer_message_mapper.map_to(parsed_offer)

    now = datetime.now(tz=pytz.UTC)

    values['updated_at'] = now
    values['created_at'] = now
    values['is_test'] = True
    values['synced'] = False

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        )
    )

    await pg.get().execute(query, *params)


def _get_commercial_options(source: Alias) -> List[bool]:
    return [
        source.c.source_object_model['category'].as_string().in_(settings.COMMERCIAL_OFFER_TASK_CREATION_CATEGORIES),
        source.c.user_segment.in_(settings.COMMERCIAL_OFFER_TASK_CREATION_SEGMENTS),
    ]


def _get_flat_options(source: Alias) -> List[bool]:
    options = []

    if settings.OFFER_TASK_CREATION_CATEGORIES:
        options.append(
            source.c.source_object_model['category'].as_string().in_(settings.OFFER_TASK_CREATION_CATEGORIES)
        )

    if settings.OFFER_TASK_CREATION_SEGMENTS:
        options.append(source.c.user_segment.in_(settings.OFFER_TASK_CREATION_SEGMENTS))

    return options


async def set_synced_and_fetch_parsed_offers_chunk(
    *,
    last_sync_date: Optional[datetime]
) -> Optional[List[ParsedOfferForCreation]]:
    po = tables.parsed_offers.alias()

    common_options = [
        po.c.source_object_model['phones'] != [],
        po.c.source_object_model['phones'] != JSON.NULL,
        po.c.source_object_model['phones'] != [''],
        not_(po.c.is_calltracking),
        not_(po.c.synced),  # TODO: удалённые объекты
    ]

    if last_sync_date:
        common_options.append(po.c.timestamp > last_sync_date)

    if settings.OFFER_TASK_CREATION_REGIONS:
        common_options.append(
            po.c.source_object_model['region'].as_integer().in_(settings.OFFER_TASK_CREATION_REGIONS)
        )

    flat_options = [*common_options, *_get_flat_options(source=po)]
    commercial_options = [*common_options, *_get_commercial_options(source=po)]

    selected_non_synced_offers_cte = (
        select([
            po,
        ])
        .where(
            or_(
                and_(*flat_options),
                and_(*commercial_options),
            )
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
            tables.parsed_offers.c.external_offer_type,
            tables.parsed_offers.c.created_at,
            tables.parsed_offers.c.user_segment,
            tables.parsed_offers.c.source_object_model['phones'].label('phones'),
            tables.parsed_offers.c.source_object_model['contact'].label('contact'),
            tables.parsed_offers.c.source_object_model['category'].as_string().label('category')
        )
    )

    rows = await pg.get().fetch(fetch_offers_query, *fetch_offers_params)
    return [parsed_offer_for_creation_mapper.map_from(row) for row in rows]


async def get_parsed_offer_for_creation_by_id(*, id: int) -> ParsedOfferForCreation:
    fetch_offer_query, fetch_offer_params = asyncpgsa.compile_query(
        select(
            [tables.parsed_offers]
        ).where(
            tables.parsed_offers.c.id == id
        ).limit(1)
    )
    row = await pg.get().fetchrow(fetch_offer_query, *fetch_offer_params)
    return parsed_offer_for_creation_mapper.map_from(row)


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
) -> None:
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
                )
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def iterate_over_parsed_offers_sorted(
    *,
    prefetch=settings.DEFAULT_PREFETCH,
) -> AsyncGenerator[ParsedOffer, None]:
    po = tables.parsed_offers.alias()
    query, params = asyncpgsa.compile_query(
        select(
            [po]
        ).where(
            and_(
                po.c.is_test == false(),
                po.c.created_at >= datetime.now(tz=pytz.UTC) - timedelta(days=1),
            )
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


async def update_offer_categories_by_offer_id(
    *,
    offer_id: str,
    category: Category,
) -> None:

    po = tables.parsed_offers
    ofc = tables.offers_for_call

    query, params = asyncpgsa.compile_query(
        update(
            ofc
        ).values(
            category=category.value,
        ).where(
            ofc.c.id == offer_id
        )
    )
    await pg.get().fetchrow(query, *params)

    query, params = asyncpgsa.compile_query(
        select([po.c.id])
        .select_from(
            po.join(
                ofc,
                po.c.id == ofc.c.parsed_id
            )
        ).where(
            ofc.c.id == offer_id
        )
    )
    parsed_offer = await pg.get().fetchrow(query, *params)
    parsed_offer_id = parsed_offer['id']

    query = f"""
    UPDATE parsed_offers
    SET source_object_model = jsonb_set(source_object_model, '{{category}}', '"{category.value}"')
    WHERE id = '{parsed_offer_id}';
    """

    await pg.get().execute(query)


async def exists_parsed_offer_by_source_object_id(
    *,
    source_object_id: str,
):
    query = f"""
    SELECT COUNT(*) FROM parsed_offers
    WHERE source_object_id = '{source_object_id}';
    """
    result = await pg.get().fetchval(query)

    return bool(result)


async def delete_test_parsed_offers() -> None:
    query, params = asyncpgsa.compile_query(
        delete(
            tables.parsed_offers
        ).where(
            tables.parsed_offers.c.is_test == true()
        )
    )
    await pg.get().execute(query, *params)
