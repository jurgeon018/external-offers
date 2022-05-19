from datetime import datetime

import asyncpgsa
from sqlalchemy import and_, insert, update

from external_offers import pg
from external_offers.repositories.postgresql.tables import hunted_client_logs


async def create_hunted_client_log(
    client_id: str,
    operator_user_id: int,
) -> None:
    query, params = asyncpgsa.compile_query(
        insert(
            hunted_client_logs
        ).values([{
            'client_id': client_id,
            'is_returned_to_waiting': False,
            'operator_user_id': operator_user_id,
            'created_at': datetime.now()
        }])
    )
    await pg.get().execute(query, *params)


async def update_hunted_client_log_status(
    client_id: str,
    operator_user_id: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            hunted_client_logs
        ).values(
            is_returned_to_waiting=True,
        ).where(
            and_(
                hunted_client_logs.c.client_id == client_id,
                hunted_client_logs.c.operator_user_id == operator_user_id,
                hunted_client_logs.c.is_returned_to_waiting.is_(False),
            )
        )
    )
    await pg.get().execute(query, *params)
