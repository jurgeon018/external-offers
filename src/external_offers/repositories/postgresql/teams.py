from typing import Optional, List
import asyncpgsa
from simple_settings import settings
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, delete, func, not_, select, update
from sqlalchemy.sql.expression import false, true
from external_offers import pg
from external_offers.enums.user_segment import UserSegment
from external_offers.entities.teams import Team, Role
from external_offers.entities.operators import Operator
from external_offers.repositories.postgresql.tables import teams
from external_offers.mappers.teams import teams_mapper


async def get_teams() -> List[Team]:
    query, params = asyncpgsa.compile_query(
        select(
            [teams]
        )
    )
    rows = await pg.get().fetch(query, *params)
    return [teams_mapper.map_from(row) for row in rows]


async def get_team_by_id(id: int) -> Optional[Team]:
    query, params = asyncpgsa.compile_query(
        select(
            [teams]
        ).where(
            teams.c.id == str(id)
        ).limit(1)
    )
    row = await pg.get().fetchrow(query, *params)
    return teams_mapper.map_from(row) if row else None


async def create_team(
    *,
    id: str,
    name: str,
    lead_id: str,
    segment: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        insert(
            teams
        ).values(
            id=id,
            name=name,
            lead_id=lead_id,
            segment=segment,
        )
    )
    await pg.get().execute(query, *params)


async def update_team_by_id(
    *,
    id: str,
    name: str,
    lead_id: str,
    segment: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            teams
        ).where(
            teams.c.id == id
        ).values(
            name=name,
            lead_id=lead_id,
            segment=segment,
        )
    )
    await pg.get().execute(query, *params)


async def delete_team_by_id(id: str) -> None:
    query, params = asyncpgsa.compile_query(
        delete(
            teams
        ).where(
            teams.c.id == id
        )
    )
    await pg.get().execute(query, *params)

