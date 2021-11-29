from datetime import datetime
from typing import AsyncGenerator, List, Optional

import asyncpgsa
import pytz
from cian_core.runtime_settings import runtime_settings
from sqlalchemy import and_, func, or_, select
from sqlalchemy.dialects.postgresql import insert

from external_offers import pg
from external_offers.entities import ClientStatus, OfferStatus
from external_offers.entities.event_log import EnrichedEventLogEntry, EventLogEntry
from external_offers.mappers.event_log import enriched_event_log_entry_mapper, event_log_entry_mapper
from external_offers.repositories.postgresql.tables import clients, event_log, offers_for_call


async def save_event_log_for_offers(
    *,
    offers_ids: List[str],
    operator_user_id: int,
    status: str,
    call_id: str,
    created_at: Optional[datetime] = None
) -> None:
    created_at = created_at or datetime.now(tz=pytz.utc)
    values = [
        {
            'offer_id': offer_id,
            'operator_user_id': operator_user_id,
            'status': status,
            'call_id': call_id,
            'created_at': created_at
        }
        for offer_id in offers_ids
    ]

    query, params = asyncpgsa.compile_query(
        insert(event_log).values(values)
    )

    await pg.get().execute(query, *params)


async def get_enriched_event_log_entries_for_drafts_kafka_sync(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> List[EnrichedEventLogEntry]:
    options = [
        event_log.c.status == OfferStatus.draft.value
    ]

    if date_from:
        options.append(func.date_trunc('day', event_log.c.created_at) >= date_from)
    if date_to:
        options.append(func.date_trunc('day', event_log.c.created_at) <= date_to)

    query, params = asyncpgsa.compile_query(
        select([
            event_log,
            clients.c.cian_user_id,
            clients.c.avito_user_id,
            clients.c.client_phones,
            offers_for_call.c.offer_cian_id
        ]).select_from(
            event_log.join(
                offers_for_call.join(
                    clients,
                    offers_for_call.c.client_id == clients.c.client_id
                ),
                event_log.c.offer_id == offers_for_call.c.id
            )
        ).where(
            and_(
                *options
            ),
        )
    )

    rows = await pg.get().fetch(query, *params)
    return [enriched_event_log_entry_mapper.map_from(row) for row in rows]


async def get_enriched_event_log_entries_for_calls_kafka_sync(
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None
) -> List[EnrichedEventLogEntry]:
    options = [
        or_(
            clients.c.status == ClientStatus.call_missed.value,
            clients.c.status == ClientStatus.declined.value,
            clients.c.status == ClientStatus.accepted.value
        ),
    ]

    if date_from:
        options.append(func.date_trunc('day', event_log.c.created_at) >= date_from)
    if date_to:
        options.append(func.date_trunc('day', event_log.c.created_at) <= date_to)

    query, params = asyncpgsa.compile_query(
        select([
            event_log,
            clients.c.cian_user_id,
            clients.c.avito_user_id,
            clients.c.client_phones,
            clients.c.status.label('client_status'),
            offers_for_call.c.offer_cian_id
        ]).distinct(
            clients.c.client_id
        ).select_from(
            event_log.join(
                offers_for_call.join(
                    clients,
                    offers_for_call.c.client_id == clients.c.client_id
                ),
                event_log.c.offer_id == offers_for_call.c.id
            )
        ).where(
            and_(
                *options
            ),
        )
    )

    rows = await pg.get().fetch(query, *params)
    return [enriched_event_log_entry_mapper.map_from(row) for row in rows]


async def iterate_over_event_logs_sorted(
    *,
    prefetch=runtime_settings.DEFAULT_PREFETCH
) -> AsyncGenerator[EventLogEntry, None]:
    query, params = asyncpgsa.compile_query(
        select([
            event_log
        ]).order_by(
            event_log.c.created_at.asc(),
            event_log.c.id.asc()
        )
    )
    cursor = await pg.get().cursor(
        query,
        *params,
        prefetch=prefetch
    )
    async for row in cursor:
        yield event_log_entry_mapper.map_from(row)
