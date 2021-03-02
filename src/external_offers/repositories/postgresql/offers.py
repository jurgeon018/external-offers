from datetime import datetime
from typing import AsyncGenerator, List, Optional

import asyncpgsa
from simple_settings import settings
from sqlalchemy import and_, delete, func, or_, outerjoin, over, select, update
from sqlalchemy.dialects.postgresql import insert

from external_offers import pg
from external_offers.entities import ClientWaitingOffersCount, EnrichedOffer, Offer
from external_offers.enums import OfferStatus
from external_offers.mappers import client_waiting_offers_count_mapper, enriched_offer_mapper, offer_mapper
from external_offers.repositories.postgresql.tables import clients, offers_for_call, parsed_offers


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


async def get_offers_in_progress_by_operator(*, operator_id: int) -> List[Offer]:
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


async def get_enriched_offers_in_progress_by_operator(*, operator_id: int) -> List[EnrichedOffer]:
    query = """
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
            ofc.status = 'inProgress'
            AND c.operator_user_id = $1
    """

    rows = await pg.get().fetch(query, operator_id)

    return [enriched_offer_mapper.map_from(row) for row in rows]


async def exists_offers_in_progress_by_operator(*, operator_id: int) -> bool:
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


async def set_waiting_offers_in_progress_by_client(
    *,
    client_id: str,
    call_id: str,
) -> List[str]:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.in_progress.value,
            last_call_id=call_id
        ).where(
            and_(
                offers_for_call.c.client_id == client_id,
                offers_for_call.c.status == OfferStatus.waiting.value,
            )
        ).returning(
            offers_for_call.c.id
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    result = await pg.get().fetch(query, *params)
    return [r['id'] for r in result]


async def set_offers_declined_by_client(*, client_id: str) -> List[str]:
    return await set_offers_status_by_client(
        client_id=client_id,
        status=OfferStatus.declined
    )


async def set_offers_call_missed_by_client(*, client_id: str) -> List[str]:
    return await set_offers_status_by_client(
        client_id=client_id,
        status=OfferStatus.call_missed
    )


async def set_offers_call_later_by_client(*, client_id: str) -> List[str]:
    return await set_offers_status_by_client(
        client_id=client_id,
        status=OfferStatus.call_later
    )


async def set_offers_status_by_client(*, client_id: str, status: OfferStatus) -> List[str]:
    sql = (
        update(
            offers_for_call
        ).values(
            status=status.value,
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


async def get_offers_parsed_ids_by_parsed_ids(*, parsed_ids: str) -> Optional[List[str]]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.parsed_id]
        ).where(
            offers_for_call.c.parsed_id.in_(parsed_ids),
        )
    )

    rows = await pg.get().fetch(query, *params)

    return rows


async def set_waiting_offers_priority_by_client_ids(*, client_ids: List[str], priority: int) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            priority=priority
        ).where(
            and_(
                offers_for_call.c.client_id.in_(client_ids),
                offers_for_call.c.status == OfferStatus.waiting.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

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
        )
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


async def delete_waiting_offers_for_call_by_client_ids(*, client_ids: List[str]) -> None:
    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.status == OfferStatus.waiting.value,
                offers_for_call.c.client_id.in_(client_ids)
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_waiting_offers_for_call_by_parsed_ids(*, parsed_ids: List[str]) -> None:
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


async def get_waiting_offer_counts_by_clients() -> List[ClientWaitingOffersCount]:
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


async def iterate_over_offers_for_call_sorted(
    *,
    prefetch=settings.DEFAULT_PREFETCH,
) -> AsyncGenerator[Offer, None]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call]
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
