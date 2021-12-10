from external_offers.entities import parsed_offers
from external_offers.repositories.postgresql.tables import phones_statuses, clients
from sqlalchemy import and_, delete, func, not_, or_, outerjoin, over, select, update
from external_offers import pg
from sqlalchemy.sql import and_, delete, func, not_, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from datetime import datetime, timedelta
from typing import AsyncGenerator, List, Optional
from external_offers.entities.phones_statuses import (
    AccountPriorities,
)
import pytz
import asyncpgsa
from external_offers.services.prioritizers.prioritize_smb import SmbAccountStatus
from external_offers.services.prioritizers.prioritize_homeowner import HomeownerAccountStatus

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


async def get_phones_statuses() -> dict[str, AccountPriorities]:
    query, params = asyncpgsa.compile_query((
        select([phones_statuses])
    ))
    rows = await pg.get().fetch(query, *params)
    # TODO: переделать цикл на запрос
    phones_statuses = {}
    for row in rows:
        phones_statuses[row['phone']] = AccountPriorities(
            smb_account_status = row['smb_account_status'],
            homeowner_account_status = row['homeowner_account_status'],
            new_cian_user_id = row['new_cian_user_id'],
        )
    return phones_statuses

