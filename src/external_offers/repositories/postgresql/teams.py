from datetime import datetime
from typing import Any, AsyncGenerator, List, Optional

import asyncpgsa
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, delete, nullslast, select, update

from external_offers import pg
from external_offers.entities.teams import Team, TeamType
from external_offers.enums.client_status import ClientStatus
from external_offers.enums.offer_status import OfferStatus
from external_offers.mappers.teams import teams_mapper
from external_offers.repositories.postgresql.tables import clients, offers_for_call, teams
from external_offers.utils.assign_suitable_offers import get_team_type_clauses
from external_offers.utils.teams import get_team_info


_CLEAR_PRIORITY = 999999999999999999


async def get_teams() -> List[Team]:
    query, params = asyncpgsa.compile_query(
        select(
            [teams]
        )
    )
    rows = await pg.get().fetch(query, *params)
    return [teams_mapper.map_from(row) for row in rows]


async def get_team_by_id(team_id: Optional[int]) -> Optional[Team]:
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
    team_type: TeamType,
) -> None:
    query, params = asyncpgsa.compile_query(
        insert(
            teams
        ).values(
            team_name=team_name,
            lead_id=lead_id,
            settings=settings,
            team_type=team_type.value,
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
            settings=settings,
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


async def get_offers_count_for_team(
    *,
    team_id: int,
) -> None:
    async with pg.get().transaction():
        team = await get_team_by_id(team_id)
        team_info = get_team_info(team)
        joined_tables, team_type_clauses = get_team_type_clauses(
            team_info=team_info
        )
        query, params = asyncpgsa.compile_query(
            select(
                [offers_for_call.c.id]
            ).select_from(
                joined_tables
            ).where(
                and_(
                    offers_for_call.c.team_priorities[str(team_id)] != str(_CLEAR_PRIORITY),
                    clients.c.unactivated.is_(False),
                    offers_for_call.c.publication_status.is_(None),
                    offers_for_call.c.status == OfferStatus.waiting.value,
                    clients.c.status == ClientStatus.waiting.value,
                    clients.c.is_test.is_(False),
                    *team_type_clauses,
                ),
            ).order_by(
                nullslast(offers_for_call.c.team_priorities[str(team_id)].asc()),
                offers_for_call.c.created_at.desc()
            )
        )
        offer_ids = await pg.get().fetch(query, *params)
        query, params = asyncpgsa.compile_query(
            update(
                teams
            ).where(
                teams.c.team_id == team_id
            ).values(
                team_waiting_offers_count_updated_at=datetime.now(),
                team_waiting_offers_count=len(offer_ids),
            )
        )
        await pg.get().execute(query, *params)
