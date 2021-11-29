from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional

import asyncpgsa
import pytz
from cian_core.runtime_settings import runtime_settings
from simple_settings import settings
from sqlalchemy import and_, delete, func, not_, or_, outerjoin, over, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import false, true

from external_offers import pg
from external_offers.entities import ClientWaitingOffersCount, EnrichedOffer, Offer
from external_offers.entities.clients import ClientDraftOffersCount
from external_offers.entities.offers import OfferForPrioritization
from external_offers.enums import OfferStatus
from external_offers.mappers import (
    client_draft_offers_count_mapper,
    client_waiting_offers_count_mapper,
    enriched_offer_mapper,
    offer_for_prioritization_mapper,
    offer_mapper,
    offers,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import Status as PublicationStatus
from external_offers.repositories.postgresql.tables import clients, offers_for_call, parsed_offers
from external_offers.services.prioritizers.build_priority import build_call_later_priority, build_call_missed_priority
from external_offers.utils import iterate_over_list_by_chunks


_REGION_FIELD = 'region'


waiting_offers_counts_cte = (
    select(
        [
            offers_for_call.c.id,
            offers_for_call.c.client_id,
            over(func.count(), partition_by=offers_for_call.c.client_id).label('waiting_offers_count')
        ]
    )
    .where(
        offers_for_call.c.status == OfferStatus.waiting.value,
    )
    .cte('waiting_offers_counts_cte')
)


async def save_offer_for_call(*, offer: Offer) -> None:
    insert_query = insert(offers_for_call)

    values = offer_mapper.map_to(offer)

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        )
    )

    await pg.get().execute(query, *params)


async def get_offers_in_progress_by_operator(*, operator_id: int) -> list[Offer]:
    query = """
        SELECT
            ofc.*
        FROM
            offers_for_call as ofc
        INNER JOIN
            clients as c
        ON
            ofc.client_id = c.client_id
        WHERE
            ofc.status = 'inProgress'
            AND c.operator_user_id = $1
    """

    rows = await pg.get().fetch(query, operator_id)

    return [offer_mapper.map_from(row) for row in rows]


async def get_enriched_offers_in_progress_by_operator(
    *,
    operator_id: int,
) -> list[EnrichedOffer]:
    status_query = """ofc.status = 'inProgress'"""
    query = f"""
        SELECT
            ofc.*,
            po.source_object_model->>'title' as title,
            po.source_object_model->>'address' as address
        FROM
            offers_for_call as ofc
        INNER JOIN
            clients as c
        ON
            ofc.client_id = c.client_id
        INNER JOIN
            parsed_offers as po
        ON
            ofc.parsed_id = po.id
        WHERE
            c.operator_user_id = $1
            AND {status_query}
    """

    rows = await pg.get().fetch(query, operator_id)

    return [enriched_offer_mapper.map_from(row) for row in rows]


async def exists_offers_in_progress_by_operator(
    *,
    operator_id: int,
) -> bool:
    query = """
        SELECT
            1
        FROM
            offers_for_call as ofc
        INNER JOIN
            clients as c
        ON
            ofc.client_id = c.client_id
        WHERE
            ofc.status = 'inProgress'
            AND c.operator_user_id = $1
        LIMIT 1
    """

    exists = await pg.get().fetchval(query, operator_id)

    return exists


async def exists_offers_in_progress_by_operator_and_offer_id(*, operator_id: int, offer_id: str) -> bool:
    query, params = asyncpgsa.compile_query(
        select(
            [1]
        ).select_from(
            offers_for_call.join(
                clients,
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).where(
            and_(
                offers_for_call.c.status == OfferStatus.in_progress.value,
                clients.c.operator_user_id == operator_id,
                offers_for_call.c.id == offer_id
            )
        ).limit(1)
    )

    exists = await pg.get().fetchval(query, *params)

    return bool(exists)


async def exists_offers_in_progress_by_client(*, client_id: str) -> bool:
    query, params = asyncpgsa.compile_query(
        select(
            [1]
        ).select_from(
            offers_for_call.join(
                clients,
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).where(
            and_(
                offers_for_call.c.status == OfferStatus.in_progress.value,
                clients.c.client_id == client_id,
            )
        ).limit(1)
    )

    exists = await pg.get().fetchval(query, *params)

    return bool(exists)


async def exists_offers_draft_by_client(*, client_id: str) -> bool:
    query, params = asyncpgsa.compile_query(
        select(
            [1]
        ).select_from(
            offers_for_call.join(
                clients,
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).where(
            and_(
                offers_for_call.c.status == OfferStatus.draft.value,
                clients.c.client_id == client_id,
            )
        ).limit(1)
    )

    exists = await pg.get().fetchval(query, *params)

    return bool(exists)


async def set_offers_in_progress_by_client(
    *,
    client_id: str,
    call_id: str,
    drafted: bool = False,
) -> list[str]:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.in_progress.value,
            last_call_id=call_id
        ).where(
            offers_for_call.c.client_id == client_id,
        ).returning(
            offers_for_call.c.id
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    result = await pg.get().fetch(query, *params)
    return [r['id'] for r in result]


async def set_offers_declined_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.declined
    )


async def set_offers_call_interrupted_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.call_interrupted
    )


async def set_offers_phone_unavailable_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.phone_unavailable
    )


async def set_offers_promo_given_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.promo_given
    )


async def set_offers_call_missed_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.call_missed,
        priority=build_call_missed_priority()
    )


async def set_offers_call_later_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.call_later,
        priority=build_call_later_priority()
    )


async def set_offers_status_and_priority_by_client(
    *,
    client_id: str,
    status: OfferStatus,
    priority: Optional[int] = None
) -> list[str]:
    values = {
        'status': status.value
    }

    if priority:
        values['priority'] = priority

    sql = (
        update(
            offers_for_call
        ).values(
            **values
        ).where(
            and_(
                offers_for_call.c.client_id == client_id,
                offers_for_call.c.status == OfferStatus.in_progress.value
            )
        ).returning(
            offers_for_call.c.id
        )
    )

    query, params = asyncpgsa.compile_query(sql)
    result = await pg.get().fetch(query, *params)

    return [r['id'] for r in result]


async def set_offer_draft_by_offer_id(*, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.draft.value,
        ).where(
            and_(
                offers_for_call.c.id == offer_id,
                offers_for_call.c.status == OfferStatus.in_progress.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def set_offer_cancelled_by_offer_id(*, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.cancelled.value,
        ).where(
            and_(
                offers_for_call.c.id == offer_id,
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def set_offer_already_published_by_offer_id(*, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.already_published.value,
        ).where(
            and_(
                offers_for_call.c.id == offer_id,
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def get_offer_by_parsed_id(*, parsed_id: str) -> Optional[Offer]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call]
        ).where(
            offers_for_call.c.parsed_id == parsed_id,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return offer_mapper.map_from(row) if row else None


async def get_offer_by_offer_id(*, offer_id: str) -> Optional[Offer]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call]
        ).where(
            offers_for_call.c.id == offer_id,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return offer_mapper.map_from(row) if row else None


async def get_offers_parsed_ids_by_parsed_ids(*, parsed_ids: list[str]) -> Optional[list[str]]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.parsed_id]
        ).where(
            offers_for_call.c.parsed_id.in_(parsed_ids),
        )
    )

    rows = await pg.get().fetch(query, *params)

    return rows


async def set_waiting_offers_priority_by_offer_ids(
    *,
    offer_ids: list[str],
    priority: int,
    team_id: Optional[int],
) -> None:
    for offer_ids_chunk in iterate_over_list_by_chunks(
        iterable=offer_ids,
        chunk_size=runtime_settings.SET_WAITING_OFFERS_PRIORITY_BY_OFFER_IDS_CHUNK
    ):
        if not team_id:
            values = {
                'priority': priority
            }
            condition = or_(
                and_(
                    offers_for_call.c.status == OfferStatus.waiting.value,
                    offers_for_call.c.id.in_(offer_ids_chunk),
                ),
                and_(
                    offers_for_call.c.publication_status == PublicationStatus.draft.value,
                    offers_for_call.c.id.in_(offer_ids_chunk),
                )
            )

        else:
            offer_ids = str(tuple(offer_ids_chunk))
            if offer_ids[-2] == ',':
                lst = list(offer_ids)
                # убирает кому в конце кортежа
                lst[-2] = ''
                offer_ids = ''.join(lst)
            sql = """
            UPDATE offers_for_call
            SET team_priorities = jsonb_set(
                coalesce(team_priorities, '{}'),
                '{%s}',
                '%s'
            )
            WHERE id IN %s AND status = 'waiting';
            """ % (
                team_id,
                priority,
                offer_ids,
            )
            await pg.get().execute(sql)
            continue
        query, params = asyncpgsa.compile_query(
            update(
                offers_for_call
            ).values(
                **values
            ).where(
                condition
            )
        )
        await pg.get().execute(query, *params)


async def get_last_sync_date() -> Optional[datetime]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.synced_at]
        ).order_by(
            offers_for_call.c.synced_at.desc()
        ).limit(1)
    )
    return await pg.get().fetchval(query, *params)


async def get_offer_cian_id_by_offer_id(*, offer_id: str) -> Optional[int]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.offer_cian_id]
        ).where(
            offers_for_call.c.id == offer_id
        ).limit(1)
    )

    return await pg.get().fetchval(query, *params)


async def set_offer_cian_id_by_offer_id(*, offer_cian_id: int, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            offer_cian_id=offer_cian_id,
        ).where(
            offers_for_call.c.id == offer_id,
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def get_offer_promocode_by_offer_id(*, offer_id: str) -> Optional[str]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.promocode]
        ).where(
            offers_for_call.c.id == offer_id
        )
    )

    return await pg.get().fetchval(query, *params)


async def set_offer_promocode_by_offer_id(*, promocode: str, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            promocode=promocode,
        ).where(
            offers_for_call.c.id == offer_id,
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def try_to_lock_offer_and_return_status(*, offer_id: str) -> Optional[str]:
    query = """
        SELECT
            status
        FROM
            offers_for_call as ofc
        WHERE
            ofc.id = $1
        FOR UPDATE SKIP LOCKED
    """

    status = await pg.get().fetchval(query, offer_id)

    return status


async def delete_waiting_offers_for_call_by_client_ids(*, client_ids: list[str]) -> None:
    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.status == OfferStatus.waiting.value,
                offers_for_call.c.client_id.in_(client_ids),
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_waiting_offers_for_call_by_parsed_ids(*, parsed_ids: list[str]) -> None:
    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.parsed_id.in_(parsed_ids),
                offers_for_call.c.status == OfferStatus.waiting.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_waiting_offers_for_call_without_parsed_offers() -> None:
    offers_and_parsed_offers = outerjoin(
            left=offers_for_call,
            right=parsed_offers,
            onclause=offers_for_call.c.parsed_id == parsed_offers.c.id
    )

    waiting_offers_without_parsed_cte = (
        select(
            [
                offers_for_call.c.id,
            ]
        )
        .select_from(
            offers_and_parsed_offers
        )
        .where(
            and_(
                offers_for_call.c.status == OfferStatus.waiting.value,
                parsed_offers.c.id.is_(None)
            )
        )
        .cte('waiting_offers_without_parsed_cte')
    )

    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.id == waiting_offers_without_parsed_cte.c.id,
                offers_for_call.c.status == OfferStatus.waiting.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_waiting_offers_for_call_with_count_off_limit() -> None:
    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.id == waiting_offers_counts_cte.c.id,
                or_(
                    settings.OFFER_TASK_CREATION_MINIMUM_OFFERS > waiting_offers_counts_cte.c.waiting_offers_count,
                    settings.OFFER_TASK_CREATION_MAXIMUM_OFFERS < waiting_offers_counts_cte.c.waiting_offers_count
                )
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_old_waiting_offers_for_call() -> None:
    max_waiting_offer_age_in_days = runtime_settings.get(
        'CLEAR_WAITING_OFFERS_FOR_CALL_AGE_IN_DAYS',
        settings.CLEAR_WAITING_OFFERS_FOR_CALL_AGE_IN_DAYS
    )
    clear_border = (
        datetime.now(pytz.utc)
        - timedelta(days=max_waiting_offer_age_in_days)
    )

    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.parsed_created_at <= clear_border,
                offers_for_call.c.status == OfferStatus.waiting.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_waiting_clients_with_count_off_limit() -> None:
    sql = (
        delete(
            clients
        ).where(
            and_(
                clients.c.client_id == waiting_offers_counts_cte.c.client_id,
                or_(
                    settings.OFFER_TASK_CREATION_MINIMUM_OFFERS > waiting_offers_counts_cte.c.waiting_offers_count,
                    settings.OFFER_TASK_CREATION_MAXIMUM_OFFERS < waiting_offers_counts_cte.c.waiting_offers_count
                )
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def get_unactivated_clients_counts_by_clients() -> Optional[list[ClientDraftOffersCount]]:
    query, params = asyncpgsa.compile_query(
        select(
            [
                offers_for_call.c.id,
                offers_for_call.c.client_id,
                offers_for_call.c.priority,
                offers_for_call.c.team_priorities,
                over(func.count(), partition_by=offers_for_call.c.client_id).label('draft_offers_count')
            ]
        ).select_from(
            clients.join(
                offers_for_call,
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).where(
            and_(
                clients.c.unactivated.is_(True),
                offers_for_call.c.publication_status == PublicationStatus.draft.value,
            )
        ).distinct(
            offers_for_call.c.client_id
        )
    )
    rows = await pg.get().fetch(query, *params)
    return [client_draft_offers_count_mapper.map_from(row) for row in rows]


async def get_waiting_offer_counts_by_clients() -> list[ClientWaitingOffersCount]:
    sql = (
        select(
            [waiting_offers_counts_cte]
        ).distinct(
            waiting_offers_counts_cte.c.client_id
        )
    )

    query, params = asyncpgsa.compile_query(sql)
    rows = await pg.get().fetch(query, *params)
    return [client_waiting_offers_count_mapper.map_from(row) for row in rows]


async def get_offers_for_prioritization_by_client_ids(
    client_ids: list[str]
) -> AsyncGenerator[OfferForPrioritization, None]:
    for client_ids_chunk in iterate_over_list_by_chunks(
        iterable=client_ids,
        chunk_size=runtime_settings.ITERATE_OVER_OFFERS_FOR_PRIORITIZATION_BY_CLIENT_IDS_CHUNK,
    ):
        query, params = asyncpgsa.compile_query(
            select(
                [offers_for_call]
            ).where(
                and_(
                    offers_for_call.c.client_id.in_(client_ids_chunk),
                    offers_for_call.c.id.isnot(None),
                    offers_for_call.c.category.isnot(None),
                )
            )
        )
        cursor = await pg.get().cursor(
            query,
            *params,
            prefetch=runtime_settings.OFFERS_FOR_PRIORITIZATION_PREFETCH,
        )
        async for row in cursor:
            yield offer_for_prioritization_mapper.map_from(row)


async def get_offers_regions_by_client_id(*, client_id: str) -> list[int]:
    query, params = asyncpgsa.compile_query(
        select(
            [
                parsed_offers.c.source_object_model[_REGION_FIELD].as_integer().label(_REGION_FIELD)
            ]
        ).select_from(
            clients.join(
                offers_for_call.join(
                    parsed_offers,
                    offers_for_call.c.parsed_id == parsed_offers.c.id
                ),
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).where(
            or_(
                and_(
                    clients.c.client_id == client_id,
                    offers_for_call.c.status == OfferStatus.waiting.value,
                ),
                and_(
                    clients.c.client_id == client_id,
                    offers_for_call.c.publication_status == PublicationStatus.draft.value,
                ),
            )
        )
    )

    rows = await pg.get().fetch(query, *params)

    return [row[_REGION_FIELD] for row in rows]


async def iterate_over_offers_for_call_sorted(
    *,
    prefetch=settings.DEFAULT_PREFETCH,
) -> AsyncGenerator[Offer, None]:
    non_final_statuses = [
        OfferStatus.waiting.value,
        OfferStatus.in_progress.value,
        OfferStatus.call_missed.value,
        OfferStatus.call_later.value,
    ]
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call]
        ).where(
            and_(
                offers_for_call.c.is_test == false(),
                or_(
                    # все обьявления в нефинальных статусах отправляются в кафку повторно
                    offers_for_call.c.status.in_(non_final_statuses),
                    # все обьявления с финальным статусом отправляются в кафку единажды
                    # (отправляются только те, которые еще не были отправлены в кафку)
                    and_(
                        offers_for_call.c.status.notin_(non_final_statuses),
                        not_(offers_for_call.c.synced_with_kafka),
                    ),
                )
            )
        ).order_by(
            offers_for_call.c.created_at.asc(),
            offers_for_call.c.id.asc()
        )
    )
    cursor = await pg.get().cursor(
        query,
        *params,
        prefetch=prefetch
    )
    async for row in cursor:
        yield offer_mapper.map_from(row)


async def sync_offers_for_call_with_kafka_by_ids(offer_ids: list[int]) -> None:
    non_final_statuses = [
        OfferStatus.waiting.value,
        OfferStatus.in_progress.value,
        OfferStatus.call_missed.value,
        OfferStatus.call_later.value,
    ]
    for offer_ids_chunk in iterate_over_list_by_chunks(
        iterable=offer_ids,
        chunk_size=runtime_settings.SYNC_OFFERS_FOR_CALL_WITH_KAFKA_BY_IDS_CHUNK
    ):
        sql = (
            update(
                offers_for_call
            ).values(
                synced_with_kafka=True
            ).where(
                and_(
                    offers_for_call.c.id.in_(offer_ids_chunk),
                    # проставляет флаг только заданиям в финальных статусах
                    offers_for_call.c.status.notin_(non_final_statuses),
                )
            )
        )
        query, params = asyncpgsa.compile_query(sql)
        await pg.get().fetch(query, *params)


async def get_offer_row_version_by_offer_cian_id(offer_cian_id: int) -> Optional[int]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.row_version]
        ).where(
            offers_for_call.c.offer_cian_id == offer_cian_id,
        ).limit(1)
    )
    row_version = await pg.get().fetchval(query, *params)
    return int(row_version) if row_version is not None else None


async def get_offer_is_test_by_offer_cian_id(offer_cian_id: int) -> int:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.is_test]
        ).where(
            offers_for_call.c.offer_cian_id == offer_cian_id,
        ).limit(1)
    )
    is_test = await pg.get().fetchval(query, *params)
    return is_test


async def get_offer_publication_status_by_offer_cian_id(offer_cian_id: Optional[int]) -> str:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.publication_status]
        ).where(
            offers_for_call.c.offer_cian_id == offer_cian_id,
        ).limit(1)
    )
    publication_status = await pg.get().fetchval(query, *params)
    return publication_status


async def set_offer_done_by_offer_cian_id(
    *,
    offer_cian_id: int,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            offers_for_call
        ).values(
            status=OfferStatus.done.value,
        ).where(
            offers_for_call.c.offer_cian_id == offer_cian_id,
        )
    )
    await pg.get().execute(query, *params)


async def set_offer_publication_status_by_offer_cian_id(
    *,
    offer_cian_id: int,
    publication_status: str,
    row_version: int,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            offers_for_call
        ).values(
            row_version=row_version,
            publication_status=publication_status,
        ).where(
            offers_for_call.c.offer_cian_id == offer_cian_id
        )
    )
    await pg.get().execute(query, *params)


async def delete_test_offers_for_call() -> None:
    query, params = asyncpgsa.compile_query(
        delete(
            offers_for_call
        ).where(
            offers_for_call.c.is_test == true(),
        )
    )
    await pg.get().execute(query, *params)


async def update_offer_comment_by_offer_id(
    *,
    offer_id: str,
    comment: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            offers_for_call
        ).values(
            comment=comment
        ).where(
            offers_for_call.c.id == offer_id,
        )
    )
    await pg.get().execute(query, *params)


async def get_offer_comment_by_offer_id(offer_id: str) -> Optional[str]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.comment]
        ).where(
            offers_for_call.c.id == offer_id
        ).limit(1)
    )
    comment = await pg.get().fetchval(query, *params)
    return comment
