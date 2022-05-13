from datetime import datetime

import asyncpgsa
from sqlalchemy import insert

from external_offers import pg
from external_offers.repositories.postgresql.tables import hunted_count_logs


async def create_hunted_count_log_by_operator(
    count: int,
    operator_user_id: int,
) -> None:
    query, params = asyncpgsa.compile_query(
        insert(
            hunted_count_logs
        ).values([{
            'count': count,
            'operator_user_id': operator_user_id,
            'created_at': datetime.now(),
        }])
    )
    await pg.get().execute(query, *params)
