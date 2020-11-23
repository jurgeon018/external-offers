from datetime import datetime
from typing import List, Optional

import asyncpgsa
import pytz
from sqlalchemy.dialects.postgresql import insert

from external_offers import pg
from external_offers.repositories.postgresql.tables import event_log


async def save_event_log_for_offers(
        offers_ids: List[str],
        operator_user_id: int,
        status: str,
        created_at: Optional[datetime] = None
) -> None:
    created_at = created_at or datetime.now(tz=pytz.utc)
    values = [
        {
            'offer_id': offer_id,
            'operator_user_id': operator_user_id,
            'status': status,
            'created_at': created_at
        }
        for offer_id in offers_ids
    ]

    query, params = asyncpgsa.compile_query(
        insert(event_log).values(values)
    )

    await pg.get().execute(query, *params)
