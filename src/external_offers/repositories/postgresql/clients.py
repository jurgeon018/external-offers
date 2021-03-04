from typing import List, Optional

import asyncpgsa
from sqlalchemy import and_, any_, delete, exists, select, update
from sqlalchemy.dialects.postgresql import insert

from external_offers import pg
from external_offers.entities import Client
from external_offers.enums import ClientStatus, OfferStatus
from external_offers.mappers import client_mapper
from external_offers.repositories.postgresql.tables import clients, offers_for_call


async def get_client_by_operator(*, operator_id: int) -> Optional[Client]:
    query = """
        SELECT
            *
        FROM
            clients as c
        WHERE
            c.operator_user_id = $1
        LIMIT 1
    """

    row = await pg.get().fetchrow(query, operator_id)

    return client_mapper.map_from(row) if row else None


async def assign_waiting_client_to_operator(*, operator_id: int) -> str:
    query = """
        WITH cte1 as (
            SELECT
                c.client_id as client_id
            FROM
                clients as c
            INNER JOIN
                offers_for_call as ofc
            ON
                ofc.client_id = c.client_id
            WHERE
                c.operator_user_id IS NULL
                AND c.status = 'waiting'
                AND ofc.status = 'waiting'
            ORDER BY
                ofc.priority NULLS LAST,
                ofc.created_at
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )


        UPDATE
            clients
        SET
            operator_user_id = $1,
            status = 'inProgress'
        FROM
            cte1
        WHERE
            clients.client_id = cte1.client_id
        RETURNING
            clients.client_id
    """

    return await pg.get().fetchval(query, operator_id)


async def assign_client_to_operator(*, client_id: str, operator_id: int) -> Optional[Client]:
    sql = (
        update(
            clients
        ).values(
            status=ClientStatus.in_progress.value,
            operator_user_id=operator_id
        ).where(
            clients.c.client_id == client_id
        ).returning(
            clients
        )
    )
    query, params = asyncpgsa.compile_query(sql)
    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def exists_waiting_client() -> bool:
    query, params = asyncpgsa.compile_query(
        select([1])
        .select_from(
            clients
        )
        .where(
            and_(
                clients.c.status == ClientStatus.waiting.value,
            )
        )
        .limit(1)
    )

    exists_client = await pg.get().fetchval(query, *params)

    return bool(exists_client)


async def set_client_to_status_and_return(*, client_id: str, status: ClientStatus) -> Optional[Client]:
    sql = (
        update(
            clients
        ).values(
            status=status.value,
            operator_user_id=None
        ).where(
            clients.c.client_id == client_id
        ).returning(
            clients
        )
    )
    query, params = asyncpgsa.compile_query(sql)
    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def set_client_to_decline_status_and_return(*, client_id: str) -> Optional[Client]:
    return await set_client_to_status_and_return(
        client_id=client_id,
        status=ClientStatus.declined
    )


async def set_client_to_waiting_status_and_return(*, client_id: str) -> Optional[Client]:
    return await set_client_to_status_and_return(
        client_id=client_id,
        status=ClientStatus.waiting
    )


async def set_client_to_call_missed_status_and_return(*, client_id: str) -> Optional[Client]:
    return await set_client_to_status_and_return(
        client_id=client_id,
        status=ClientStatus.call_missed
    )


async def set_client_to_call_later_status_and_return(*, client_id: str) -> Optional[Client]:
    return await set_client_to_status_and_return(
        client_id=client_id,
        status=ClientStatus.call_later
    )


async def save_client(*, client: Client) -> None:
    insert_query = insert(clients)

    values = client_mapper.map_to(client)

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        )
    )

    await pg.get().execute(query, *params)


async def get_client_by_avito_user_id(*, avito_user_id: str) -> Optional[Client]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients]
        ).where(
            clients.c.avito_user_id == avito_user_id,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def get_client_id_by_offer_id(*, offer_id: str) -> str:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.client_id]
        ).where(
            offers_for_call.c.id == offer_id,
        ).limit(1)
    )

    return await pg.get().fetchval(query, *params)


async def get_client_by_client_id(*, client_id: str) -> Optional[Client]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients]
        ).where(
            clients.c.client_id == client_id,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def get_client_for_update_by_phone_number(*, phone_number: str) -> Optional[Client]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients],
        ).with_for_update(
            skip_locked=True
        ).where(
            any_(clients.c.client_phones) == phone_number,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def get_cian_user_id_by_client_id(*, client_id: str) -> Optional[int]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients.c.cian_user_id]
        ).where(
            clients.c.client_id == client_id,
        ).limit(1)
    )

    return await pg.get().fetchval(query, *params)


async def get_segment_by_client_id(*, client_id: str) -> Optional[str]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients.c.segment]
        ).where(
            clients.c.client_id == client_id,
        ).limit(1)
    )

    return await pg.get().fetchval(query, *params)


async def set_cian_user_id_by_client_id(*, cian_user_id: int, client_id: str):
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            cian_user_id=cian_user_id
        ).where(
            clients.c.client_id == client_id,
        )
    )

    await pg.get().execute(query, *params)


async def set_phone_number_by_client_id(*, client_id: str, phone_number: str):
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            client_phones=[phone_number]
        ).where(
            clients.c.client_id == client_id,
        )
    )

    await pg.get().execute(query, *params)


async def set_client_accepted_and_no_operator_if_no_offers_in_progress(*, client_id: str) -> bool:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            status=ClientStatus.accepted.value,
            operator_user_id=None
        ).where(
            and_(
                clients.c.client_id == client_id,
                ~exists(
                    select(
                        [1]
                    ).where(
                        and_(
                            offers_for_call.c.client_id == client_id,
                            offers_for_call.c.status == OfferStatus.in_progress.value
                        )
                    )
                )
            )
        ).returning(
            clients.c.client_id
        )
    )

    client_id = await pg.get().fetchval(query, *params)

    return bool(client_id)


async def delete_waiting_clients_by_client_ids(*, client_ids: List[str]) -> None:
    sql = (
        delete(
            clients
        ).where(
            and_(
                clients.c.status == ClientStatus.waiting.value,
                clients.c.client_id.in_(client_ids)
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)
