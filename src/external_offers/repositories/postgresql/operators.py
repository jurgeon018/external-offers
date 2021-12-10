from datetime import datetime
from typing import AsyncGenerator, List, Optional, Union

import asyncpgsa
import pytz
from cian_core.runtime_settings import runtime_settings
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
        WHERE operators.operator_id IS NOT NULL
        ORDER BY operator_id asc;
    """)
    return [enriched_operators_mapper.map_from(row) for row in rows]


async def get_enriched_teamleads() -> List[EnrichedOperator]:
    rows = await pg.get().fetch("""
        SELECT * FROM operators
        LEFT OUTER JOIN teams ON operators.team_id = teams.team_id
        WHERE operators.operator_id IS NOT NULL
        AND operators.is_teamlead
        ORDER BY operator_id asc;
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
    row = await pg.get().fetchrow("""
        SELECT * FROM operators
        LEFT OUTER JOIN teams ON operators.team_id = teams.team_id
        WHERE operators.operator_id = $1
        LIMIT 1;
    """, str(operator_id))
    return enriched_operators_mapper.map_from(row) if row else None


async def create_operator(
    *,
    operator_id: Union[int, str],
    full_name: Optional[str] = None,
    team_id: Optional[int] = None,
    email: Optional[str] = None,
    is_teamlead: bool = False,
) -> None:
    now = datetime.now(tz=pytz.utc)
    query, params = asyncpgsa.compile_query(
        insert(
            operators
        ).values(
            operator_id=str(operator_id),
            full_name=full_name,
            team_id=team_id,
            email=email,
            is_teamlead=is_teamlead,
            created_at=now,
            updated_at=now,
        )
    )
    await pg.get().execute(query, *params)


async def update_operator_by_id(
    *,
    operator_id: Union[str, int],
    full_name: str,
    team_id: Optional[int],
    email: Optional[str] = None,
    is_teamlead: bool = None,
) -> None:
    now = datetime.now(tz=pytz.utc)
    values = {
        'full_name': full_name,
        'team_id': team_id,
        'email': email,
        'updated_at': now,
    }
    if is_teamlead is not None:
        values['is_teamlead'] = is_teamlead
    query, params = asyncpgsa.compile_query(
        update(
            operators
        ).where(
            operators.c.operator_id == str(operator_id)
        ).values(
            **values
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


async def get_operator_team_id(operator_id: int) -> Optional[int]:
    query, params = asyncpgsa.compile_query(
        select([
            operators.c.team_id,
        ]).where(
            operators.c.operator_id == str(operator_id)
        ).limit(1)
    )
    operator_team_id = await pg.get().fetchval(query, *params)
    return int(operator_team_id) if operator_team_id else None


async def iterate_over_operators_sorted(
    *,
    prefetch: int = runtime_settings.DEFAULT_PREFETCH,
) -> AsyncGenerator[Operator, None]:
    query, params = asyncpgsa.compile_query(
        select(
            [operators]
        ).order_by(
            operators.c.operator_id.asc()
        )
    )
    cursor = await pg.get().cursor(
        query,
        *params,
        prefetch=prefetch
    )
    async for row in cursor:
        yield operators_mapper.map_from(row)
