from typing import Any, AsyncGenerator, List, Optional

import asyncpgsa
from cian_core.runtime_settings import runtime_settings
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import delete, select, update

from external_offers import pg
from external_offers.entities.teams import Team
from external_offers.mappers.teams import teams_mapper
from external_offers.repositories.postgresql.tables import teams


async def get_teams() -> List[Team]:
    query, params = asyncpgsa.compile_query(
        select(
            [teams]
        )
    )
    rows = await pg.get().fetch(query, *params)
    return [teams_mapper.map_from(row) for row in rows]


async def get_team_by_id(team_id: int) -> Optional[Team]:
    query, params = asyncpgsa.compile_query(
        select(
            [teams]
        ).where(
            teams.c.team_id == team_id
        ).order_by(
            teams.c.team_id.asc()
        ).limit(1)
    )
    row = await pg.get().fetchrow(query, *params)
    return teams_mapper.map_from(row) if row else None


async def create_team(
    *,
    team_name: str,
    lead_id: str,
    settings: dict[str, Any],
) -> None:
    query, params = asyncpgsa.compile_query(
        insert(
            teams
        ).values(
            team_name=team_name,
            lead_id=lead_id,
            settings=settings,
        )
    )
    await pg.get().execute(query, *params)


async def update_team_by_id(
    *,
    team_id: int,
    team_name: str,
    lead_id: str,
    settings: Optional[dict] = None,
) -> None:
    if settings is None:
        settings = {}
    query, params = asyncpgsa.compile_query(
        update(
            teams
        ).where(
            teams.c.team_id == team_id
        ).values(
            team_name=team_name,
            lead_id=lead_id,
            settings=settings
        )
    )
    await pg.get().execute(query, *params)


async def delete_team_by_id(team_id: int) -> None:
    query, params = asyncpgsa.compile_query(
        delete(
            teams
        ).where(
            teams.c.team_id == team_id
        )
    )
    await pg.get().execute(query, *params)


async def iterate_over_teams_sorted(
    *,
    prefetch: int
) -> AsyncGenerator[Team, None]:
    query, params = asyncpgsa.compile_query(
        select([
            teams
        ]).order_by(
            teams.c.team_id.asc()
        )
    )
    cursor = await pg.get().cursor(
        query,
        *params,
        prefetch=prefetch
    )
    async for row in cursor:
        yield teams_mapper.map_from(row)
