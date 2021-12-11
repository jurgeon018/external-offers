from datetime import datetime, timedelta
from typing import Optional, Any, Union
from cian_core.runtime_settings import runtime_settings
import asyncpgsa
import pytz
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import select

from external_offers import pg
from external_offers.entities.phones_statuses import ClientAccountStatus
from external_offers.repositories.postgresql import tables
from external_offers.services.prioritizers.prioritize_homeowner import HomeownerAccountStatus
from external_offers.services.prioritizers.prioritize_smb import SmbAccountStatus


async def get_phones_statuses() -> dict[str, ClientAccountStatus]:
    phones_statuses = tables.phones_statuses.alias()

    query, params = asyncpgsa.compile_query((
        select([phones_statuses])
    ))
    rows = await pg.get().fetch(query, *params)
    phones_statuses = {}
    for row in rows:
        # такая вложеность нужна для того чтобы при приоретизации клиента по номеру телефона
        # не ходить в базу на каждой итерации,
        # а доставать инфу про статусы акаунтов из словаря за O(1) по номеру телефона(ключ)
        phones_statuses[row['phone']] = ClientAccountStatus(
            smb_account_status=row['smb_account_status'],
            homeowner_account_status=row['homeowner_account_status'],
            new_cian_user_id=row['new_cian_user_id'],
        )
    return phones_statuses


async def set_phone_statuses(
    values: dict[str, Union[datetime, str, SmbAccountStatus, HomeownerAccountStatus, Optional[int]]]
) -> None:
    phones_statuses = tables.phones_statuses
    insert_query = insert(phones_statuses)

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        )
        .on_conflict_do_update(
            index_elements=[
                phones_statuses.c.phone,
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


async def get_recently_cashed_phone_numbers() -> list[int]:
    """достает все номера телефонов по которым были обновления за последние 5 дней"""
    phones_statuses = tables.phones_statuses.alias()
    days = runtime_settings.get('PHONES_STATUSES_UPDATE_CHECK_WINDOW_IN_DAYS', 5)
    updated_at_border = datetime.now(tz=pytz.UTC) - timedelta(days=days)
    query, params = asyncpgsa.compile_query(
        select([
            phones_statuses.c.phone,
        ]).where(
            phones_statuses.c.updated_at > updated_at_border
        )
    )
    rows = await pg.get().fetch(query, *params)
    return [row['phone'] for row in rows]
