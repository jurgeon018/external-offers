from typing import Optional

import asyncpgsa
from sqlalchemy import update

from external_offers import pg
from external_offers.entities import Client
from external_offers.enums import ClientStatus
from external_offers.mappers import client_mapper
from external_offers.repositories.postgresql.tables import clients


async def get_client_by_operator(operator_id: int) -> Optional[Client]:
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


async def assign_waiting_client_to_operator(operator_id: int) -> int:
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


async def set_client_to_decline_status(client_id: int) -> None:
    sql = (
        update(
            clients
        ).values(
            status=ClientStatus.declined.value,
            operator_user_id=None
        ).where(
            clients.c.client_id == client_id
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    return await pg.get().execute(query, *params)
