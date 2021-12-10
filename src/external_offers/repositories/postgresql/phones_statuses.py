from datetime import datetime
from typing import Optional

import asyncpgsa
import pytz
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql import select

from external_offers import pg
from external_offers.entities.phones_statuses import PhoneStatuses
from external_offers.repositories.postgresql.tables import phones_statuses
from external_offers.services.prioritizers.prioritize_homeowner import HomeownerAccountStatus
from external_offers.services.prioritizers.prioritize_smb import SmbAccountStatus


async def get_phones_statuses() -> dict[str, PhoneStatuses]:
    query, params = asyncpgsa.compile_query((
        select([phones_statuses])
    ))
    rows = await pg.get().fetch(query, *params)
    phones_statuses = {}
    for row in rows:
        # такая вложеность нужна для того чтобы при приоретизации клиента по номеру телефона
        # не ходить в базу на каждой итерации, 
        # а доставать инфу про статусы акаунтов из словаря за O(1) по номеру телефона(ключ)
        phones_statuses[row['phone']] = PhoneStatuses(
            smb_account_status=row['smb_account_status'],
            homeowner_account_status=row['homeowner_account_status'],
            new_cian_user_id=row['new_cian_user_id'],
        )
    return phones_statuses


async def set_phone_statuses(
    *,
    phone: str,
    smb_account_status: SmbAccountStatus,
    homeowner_account_status: HomeownerAccountStatus,
    new_cian_user_id: Optional[int],
) -> None:
    insert_query = insert(phones_statuses)

    now = datetime.now(tz=pytz.UTC)

    values = {}
    values['created_at'] = now
    values['updated_at'] = now
    values['phone'] = phone
    values['smb_account_status'] = smb_account_status
    values['homeowner_account_status'] = homeowner_account_status
    values['new_cian_user_id'] = new_cian_user_id

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        ).on_conflict_do_update(
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
