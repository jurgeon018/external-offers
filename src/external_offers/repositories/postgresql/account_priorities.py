from external_offers.entities import parsed_offers
from external_offers.repositories.postgresql.tables import account_priorities, clients
from sqlalchemy import and_, delete, func, not_, or_, outerjoin, over, select, update
from external_offers import pg
from sqlalchemy.sql import and_, delete, func, not_, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timedelta
from typing import AsyncGenerator, List, Optional
from external_offers.entities.account_priorities import (
    AccountPriority,
)
from external_offers.mappers.account_priorities import (
    account_priority_mapper,
)
from external_offers.utils import iterate_over_list_by_chunks
import pytz
import asyncpgsa


async def get_latest_updated_at() -> Optional[datetime]:
    query, params = asyncpgsa.compile_query(
        select([
            func.max(account_priorities.c.updated),
        ]).limit(1)
    )
    return await pg.get().fetchval(query, *params)


async def set_account_priority_by_client_id(
    *,
    client_id: str,    
    team_id: int,
    account_priority: int,
) -> None:
    insert_query = insert(account_priorities)

    now = datetime.now(tz=pytz.UTC)

    values = {}
    values['client_id'] = client_id
    values['team_id'] = team_id
    values['priority'] = account_priority
    values['created_at'] = now
    values['updated_at'] = now
    
    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        ).on_conflict_do_update(
            index_elements=[
                account_priorities.c.team_id,
                account_priorities.c.client_id,
            ],
            set_={
                'client_id': insert_query.excluded.client_id,
                'team_id': insert_query.excluded.team_id,
                'priority': insert_query.excluded.priority,
                'updated_at': insert_query.excluded.updated_at,
            }
        )
    )
    await pg.get().execute(query, *params)


async def delete_account_priorities_without_clients() -> None:
    account_priorities_without_parsed_cte = (
        select([account_priorities.c.id])
        .select_from(
            outerjoin(
                left=account_priorities,
                right=clients,
                onclause=account_priorities.c.parsed_id == clients.c.client_id
            )
        ).where(
            clients.c.client_id.is_(None)
        ).cte('account_priorities_without_parsed_cte')
    )
    query, params = asyncpgsa.compile_query((
        delete(
            account_priorities
        ).where(
            account_priorities.c.priority_id == account_priorities_without_parsed_cte.c.id
        )
    ))
    await pg.get().execute(query, *params)
