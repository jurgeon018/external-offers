from typing import Optional

from external_offers import pg
from external_offers.entities import Client
from external_offers.mappers import client_mapper


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
