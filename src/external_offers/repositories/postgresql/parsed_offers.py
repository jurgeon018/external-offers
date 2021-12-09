from datetime import datetime, timedelta
from typing import AsyncGenerator, List, Optional

import asyncpgsa
import pytz
from cian_core.runtime_settings import runtime_settings as settings
from cian_json import json
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, delete, func, not_, or_, select, update
from sqlalchemy.sql.expression import false, true

from external_offers import pg
from external_offers.entities.parsed_offers import (
    ParsedObjectModel,
    ParsedOffer,
    ParsedOfferForCreation,
    ParsedOfferMessage,
)
from external_offers.entities.teams import Team
from external_offers.enums.offer_status import OfferStatus
from external_offers.mappers.parsed_object_model import parsed_object_model_mapper
from external_offers.mappers.parsed_offers import (
    parsed_offer_for_creation_mapper,
    parsed_offer_mapper,
    parsed_offer_message_mapper,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import Category
from external_offers.repositories.postgresql import tables
from external_offers.utils import iterate_over_list_by_chunks


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


async def get_parsed_ids_for_cleaning(
    *,
    team: Optional[Team],
    is_test: Optional[bool] = None,
) -> list[str]:
    po = tables.parsed_offers.alias()
    if team:
        team_settings = team.get_settings()
        regions = team_settings['regions']
        user_segments = team_settings['segments']
        categories = team_settings['categories']
    else:
        regions = settings.OFFER_TASK_CREATION_REGIONS
        user_segments = settings.OFFER_TASK_CREATION_SEGMENTS
        categories = settings.OFFER_TASK_CREATION_CATEGORIES
    regions = [str(region) for region in regions]
    options = or_(
        po.c.user_segment.notin_(user_segments),
        # po.c.source_object_model['user_segment'].as_string().notin_(user_segments),
        po.c.source_object_model['region'].as_string().notin_(regions),
        po.c.source_object_model['category'].as_string().notin_(categories),
    )
    if isinstance(is_test, bool):
        options = and_(
            po.c.is_test == is_test,
            options,
        )
    query, params = asyncpgsa.compile_query(
        select([
            po.c.id,
        ])
        .where(
            options
        )
    )
    rows = await pg.get().fetch(query, *params)
    parsed_ids = [row['id'] for row in rows]
    return parsed_ids


async def set_synced_and_fetch_parsed_offers_chunk(
    *,
    last_sync_date: Optional[datetime]
) -> Optional[List[ParsedOfferForCreation]]:

    po = tables.parsed_offers.alias()

    options = [
        po.c.source_object_model['phones'] != [],
        po.c.source_object_model['phones'] != JSON.NULL,
        po.c.source_object_model['phones'] != [''],
        po.c.source_user_id.isnot(None),
        not_(po.c.is_calltracking),
        not_(po.c.synced),
    ]
    if last_sync_date:
        options.append(po.c.timestamp > last_sync_date)

    selected_non_synced_offers_cte = (
        select([
            po,
        ])
        .where(
            and_(
                *options,
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
            tables.parsed_offers.c.source_group_id,
            tables.parsed_offers.c.timestamp,
            tables.parsed_offers.c.external_offer_type,
            tables.parsed_offers.c.created_at,
            tables.parsed_offers.c.user_segment,
            tables.parsed_offers.c.user_subsegment,
            tables.parsed_offers.c.source_object_model['phones'].label('phones'),
            tables.parsed_offers.c.source_object_model['contact'].label('contact'),
            tables.parsed_offers.c.source_object_model['category'].as_string().label('category')
        )
    )

    rows = await pg.get().fetch(fetch_offers_query, *fetch_offers_params)
    return [parsed_offer_for_creation_mapper.map_from(row) for row in rows]


async def get_parsed_offers_for_account_prioritization() -> list:

    po = tables.parsed_offers.alias()

    selected_non_synced_offers_cte = (
        select([
            po,
        ])
        .where(
            and_(
                po.c.source_object_model['phones'] != [],
                po.c.source_object_model['phones'] != JSON.NULL,
                po.c.source_object_model['phones'] != [''],
                po.c.source_user_id.isnot(None),
                not_(po.c.is_calltracking),
                not_(po.c.synced),
            )
        )
        .limit(settings.OFFER_TASK_CREATION_OFFER_FETCH_LIMIT)
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
        ]).where(
            and_(
                po.c.is_test.isnot(True),
                po.c.external_offer_type.is_distinct_from('commercial'),
            ),
        ).limit(1)
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
    ofc = tables.offers_for_call.alias()

    query, params = asyncpgsa.compile_query(
        select([
            ofc.c.parsed_id
        ]).where(
            ofc.c.status.in_([
                OfferStatus.in_progress.value,
                OfferStatus.call_missed.value,
                OfferStatus.call_later.value,
            ])
        )
    )
    parsed_ids_of_offers_in_nonfinal_status = await pg.get().fetch(query, *params)
    parsed_ids = [row['parsed_id'] for row in parsed_ids_of_offers_in_nonfinal_status]
    if parsed_ids:
        for parsed_ids_chunk in iterate_over_list_by_chunks(
            iterable=parsed_ids,
            chunk_size=settings.DELETE_OLD_OFFERS_CHUNK,
        ):
            query, params = asyncpgsa.compile_query(
                delete(
                    po
                ).where(
                    and_(
                        po.c.updated_at < updated_at_border,
                        po.c.id.notin_(parsed_ids_chunk)
                    )
                )
            )
            await pg.get().execute(query, *params)
    else:
        query, params = asyncpgsa.compile_query(
            delete(
                po
            ).where(
                po.c.updated_at < updated_at_border,
            )
        )
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