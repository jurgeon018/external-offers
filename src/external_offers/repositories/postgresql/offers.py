from typing import List

from external_offers import pg
from external_offers.entities import Offer
from external_offers.mappers import offer_mapper


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
            status = 'inProgress'
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
            EXISTS(
                SELECT
                    ofc.*
                FROM
                    offers_for_call as ofc
                INNER JOIN
                    clients as c
                ON
                    ofc.client_id = c.client_id
                WHERE
                    status = 'inProgress'
                    AND c.operator_user_id = $1
            )
    """

    exists = await pg.get().fetchval(query, operator_id)

    return exists
