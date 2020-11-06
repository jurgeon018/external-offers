from typing import List

import asyncpgsa
from sqlalchemy import and_, select, update

from external_offers import pg
from external_offers.entities import Offer
from external_offers.enums import OfferStatus
from external_offers.mappers import offer_mapper
from external_offers.repositories.postgresql.tables import clients, offers_for_call


async def get_offers_in_progress_by_operator(operator_id: int) -> List[Offer]:
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


async def set_waiting_offers_in_progress_by_client(client_id: int) -> None:
    query = """
        UPDATE
            offers_for_call
        SET
            status='inProgress'
        WHERE
            status = 'waiting'
            AND client_id = $1;
    """

    await pg.get().execute(query, client_id)


async def exists_offers_in_progress_by_operator(operator_id: int) -> bool:
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


async def exists_offers_in_progress_by_operator_and_offer_id(operator_id: int, offer_id: int) -> bool:
    query, params = asyncpgsa.compile_query(
        select([1])
        .select_from(
            offers_for_call.join(
                clients,
                offers_for_call.c.client_id == clients.c.client_id
            )
        )
        .where(
            and_(
                offers_for_call.c.status == OfferStatus.in_progress.value,
                clients.c.operator_user_id == operator_id,
                offers_for_call.c.id == int(offer_id)
                )
        )
        .limit(1)
    )

    exists = await pg.get().fetchval(query, *params)

    return bool(exists)


async def set_offers_declined_by_client(client_id: int) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.declined.value,
        ).where(
            and_(
                offers_for_call.c.client_id == client_id,
                offers_for_call.c.status == OfferStatus.in_progress.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def set_offers_call_missed_by_client(client_id: int) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.call_missed.value,
        ).where(
            and_(
                offers_for_call.c.client_id == client_id,
                offers_for_call.c.status == OfferStatus.in_progress.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)
