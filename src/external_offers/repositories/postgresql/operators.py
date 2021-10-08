from datetime import datetime
from typing import List, Optional, Union

import asyncpgsa
import pytz
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import delete, func, select, update

from external_offers import pg
from external_offers.entities import EnrichedOperator, Operator
from external_offers.mappers.teams import enriched_operators_mapper, operators_mapper
from external_offers.repositories.postgresql.tables import operators


async def get_operators() -> List[Operator]:
    query, params = asyncpgsa.compile_query(
        select(
            [operators]
        )
    )
    rows = await pg.get().fetch(query, *params)
    return [operators_mapper.map_from(row) for row in rows]


async def get_enriched_operators() -> List[EnrichedOperator]:
    rows = await pg.get().fetch("""
        SELECT * FROM operators
        LEFT OUTER JOIN teams ON operators.team_id = teams.team_id
        WHERE operators.operator_id IS NOT NULL;
    """)
    return [enriched_operators_mapper.map_from(row) for row in rows]


async def get_operator_by_id(operator_id: int) -> Optional[Operator]:
    query, params = asyncpgsa.compile_query(
        select(
            [operators]
        ).where(
            operators.c.operator_id == str(operator_id)
        ).limit(1)
    )
    row = await pg.get().fetchrow(query, *params)
    return operators_mapper.map_from(row) if row else None


async def get_enriched_operator_by_id(operator_id: Union[str, int]) -> Optional[EnrichedOperator]:
    row = await pg.get().fetchrow(f"""
        SELECT * FROM operators
        LEFT OUTER JOIN teams ON operators.team_id = teams.team_id
        WHERE operators.operator_id = '{operator_id}'
        LIMIT 1;
    """)
    return enriched_operators_mapper.map_from(row) if row else None


async def create_operator(
    *,
    operator_id: Union[int, str],
    full_name: Optional[str] = None,
    team_id: Optional[int] = None,
    is_teamlead: bool = False,
    email: Optional[str] = None,
) -> None:
    now = datetime.now(tz=pytz.utc)
    query, params = asyncpgsa.compile_query(
        insert(
            operators
        ).values(
            operator_id=str(operator_id),
            full_name=full_name,
            team_id=team_id,
            is_teamlead=is_teamlead,
            email=email,
            created_at=now,
            updated_at=now,
        )
    )
    await pg.get().execute(query, *params)


async def update_operator_by_id(
    *,
    operator_id: Union[str, int],
    full_name: str,
    team_id: str,
    is_teamlead: bool = False,
    email: Optional[str] = None,
) -> None:
    now = datetime.now(tz=pytz.utc)
    query, params = asyncpgsa.compile_query(
        update(
            operators
        ).where(
            operators.c.operator_id == str(operator_id)
        ).values(
            full_name=full_name,
            team_id=team_id,
            email=email,
            is_teamlead=is_teamlead,
            updated_at=now
        )
    )
    await pg.get().execute(query, *params)


async def delete_operator_by_id(operator_id: str):
    query, params = asyncpgsa.compile_query(
        delete(
            operators
        ).where(
            operators.c.operator_id == operator_id
        )
    )
    await pg.get().execute(query, *params)


async def get_latest_operator_updating() -> Optional[datetime]:
    query, params = asyncpgsa.compile_query(
        select([
            func.max(operators.c.updated_at)
        ]).limit(1)
    )
    return await pg.get().fetchval(query, *params)
