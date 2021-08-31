import asyncpgsa
from simple_settings import settings
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, delete, func, not_, select, update
from sqlalchemy.sql.expression import false, true
from external_offers import pg
from external_offers.repositories.postgresql.tables import (
    roles,
    teams,
    operators,
)


async def create_team(
    *,
    name: str,
    role_id: int,
    settings: dict,
):
    query, params = asyncpgsa.compile_query(
        insert(
            teams
        ).values(
            name=name,
            role_id=role_id,
            settings=settings,
        )
    )
    return await pg.get().execute(query, *params)
