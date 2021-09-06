from typing import Optional, List
import asyncpgsa
from simple_settings import settings
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, delete, func, not_, select, update
from sqlalchemy.sql.expression import false, true
from external_offers import pg
from external_offers.enums.user_segment import UserSegment
from external_offers.entities import Operator
from external_offers.repositories.postgresql.tables import operators
from external_offers.mappers.teams import operators_mapper


async def get_operators() -> List[Operator]:
    query, params = asyncpgsa.compile_query(
        select(
            [operators]
        )
    )
    rows = await pg.get().fetch(query, *params)
    return [operators_mapper.map_from(row) for row in rows]


async def get_operator_by_id(id: int) -> Optional[Operator]:
    query, params = asyncpgsa.compile_query(
        select(
            [operators]
        ).where(
            operators.c.id == str(id)
        ).limit(1)
    )
    row = await pg.get().fetchrow(query, *params)
    return operators_mapper.map_from(row) if row else None


async def create_operator(
    *,
    id: int,
    name: str,
    team_id: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        insert(
            operators
        ).values(
            id=id,
            name=name,
            team_id=team_id,
        )
    )
    await pg.get().execute(query, *params)


async def update_operator_by_id(
    *,
    id: str,
    name: str,
    team_id: str
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            operators
        ).where(
            operators.c.id == id
        ).values(
            name=name,
            team_id=team_id,
        )
    )
    await pg.get().execute(query, *params)


async def delete_operator_by_id(id: str):
    query, params = asyncpgsa.compile_query(
        delete(
            operators
        ).where(
            operators.c.id == id
        )
    )
    await pg.get().execute(query, *params)


async def update_operators_team(
    *,
    operators_id: List[int],
    team_id: int,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            operators
        ).values(
            team_id=team_id
        ).where(
            operators.c.id.in_(operators_id)
        )
    )
    await pg.get().execute(query, *params)

