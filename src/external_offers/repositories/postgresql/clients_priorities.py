from datetime import datetime, timedelta
from typing import Optional

import asyncpgsa
import pytz
from cian_core.runtime_settings import runtime_settings
from cian_json import json
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import and_, select

from external_offers import pg
from external_offers.repositories.postgresql import tables


async def get_clients_priority_by_team_id(
    team_id: Optional[int] = None,
) -> Optional[dict[str, str]]:
    clients_priorities = tables.clients_priorities.alias()
    now = datetime.now(tz=pytz.UTC)
    hours = runtime_settings.get('CLIENTS_PRIORITIES_CREATED_AT_BORDER_HOURS', 6)
    created_at_border = now - timedelta(hours=hours)
    query, params = asyncpgsa.compile_query(
        select(
            [
                clients_priorities.c.priorities
            ]
        ).where(
            and_(
                clients_priorities.c.created_at > created_at_border,
                clients_priorities.c.team_id == team_id,
            )
        ).limit(1)
    )
    cached_clients_priority = await pg.get().fetchval(query, *params)
    if cached_clients_priority:
        cached_clients_priority = json.loads(cached_clients_priority)
    return cached_clients_priority


async def save_clients_priority(
    *,
    clients_priority: dict[str, str],
    team_id: Optional[int] = None,
) -> None:
    insert_query = insert(tables.clients_priorities)
    now = datetime.now(tz=pytz.UTC)
    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [
                {
                    'priorities': clients_priority,
                    'team_id': team_id,
                    'created_at': now,
                    'updated_at': now,
                }
            ]
        )
    )
    await pg.get().execute(query, *params)
