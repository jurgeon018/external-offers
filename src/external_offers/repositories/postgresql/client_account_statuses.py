from datetime import datetime, timedelta
from operator import and_
from typing import Optional, Union
from sqlalchemy import JSON

import asyncpgsa
import pytz
from cian_core.runtime_settings import runtime_settings
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import select
from sqlalchemy.sql.operators import isnot

from external_offers import pg
from external_offers.entities.client_account_statuses import ClientAccountStatus
from external_offers.mappers.client_account_statuses import client_account_status_mapper
from external_offers.repositories.postgresql import tables
from external_offers.services.prioritizers.prioritize_homeowner import HomeownerAccountStatus
from external_offers.services.prioritizers.prioritize_smb import SmbAccountStatus


async def get_client_account_statuses() -> dict[str, ClientAccountStatus]:
    client_account_statuses = tables.client_account_statuses.alias()

    query, params = asyncpgsa.compile_query((
        select([
            client_account_statuses
        ]).where(
            and_(
                client_account_statuses.c.smb_account_status.isnot(None),
                client_account_statuses.c.homeowner_account_status.isnot(None),
                client_account_statuses.c.smb_account_status != JSON.NULL,
                client_account_statuses.c.homeowner_account_status != JSON.NULL,
            )
        )
    ))
    rows = await pg.get().fetch(query, *params)
    client_account_statuses = {}
    for row in rows:
        # такая вложеность нужна для того чтобы при приоретизации клиента по номеру телефона
        # не ходить в базу на каждой итерации,
        # а доставать инфу про статусы акаунтов из словаря за O(1) по номеру телефона(ключ)
        client_account_statuses[row['phone']] = client_account_status_mapper.map_from(row)
    return client_account_statuses


async def set_client_account_status(
    values: dict[str, Union[datetime, str, SmbAccountStatus, HomeownerAccountStatus, Optional[int]]]
) -> None:
    client_account_statuses = tables.client_account_statuses
    insert_query = insert(client_account_statuses)

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        )
        .on_conflict_do_update(
            index_elements=[
                client_account_statuses.c.phone,
            ],
            set_={
                'updated_at': insert_query.excluded.updated_at,
                'phone': insert_query.excluded.phone,
                'smb_account_status': insert_query.excluded.smb_account_status,
                'homeowner_account_status': insert_query.excluded.homeowner_account_status,
                'new_cian_user_id': insert_query.excluded.new_cian_user_id,
            }
        )
    )
    await pg.get().execute(query, *params)


async def get_recently_cached_client_account_statuses() -> list[str]:
    """достает все номера телефонов по которым были обновления за последние 5 дней"""
    client_account_statuses = tables.client_account_statuses.alias()
    days = runtime_settings.get('CLIENT_ACCOUNT_STATUSES_UPDATE_CHECK_WINDOW_IN_DAYS', 5)
    updated_at_border = datetime.now(tz=pytz.UTC) - timedelta(days=days)
    query, params = asyncpgsa.compile_query(
        select([
            client_account_statuses.c.phone,
        ]).where(
            client_account_statuses.c.updated_at > updated_at_border
        )
    )
    rows = await pg.get().fetch(query, *params)
    return [row['phone'] for row in rows]
