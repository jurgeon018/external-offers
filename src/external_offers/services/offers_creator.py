import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

import pytz
from cian_core.context import new_operation_id
from cian_core.runtime_settings import runtime_settings
from cian_json import json
from simple_settings import settings
from tornado import gen

from external_offers import pg
from external_offers.entities import Offer
from external_offers.entities.clients import Client, ClientStatus
from external_offers.enums import UserSegment
from external_offers.helpers.uuid import generate_guid
from external_offers.repositories.postgresql import (
    delete_old_waiting_offers_for_call,
    delete_waiting_clients_by_client_ids,
    delete_waiting_clients_with_count_off_limit,
    delete_waiting_offers_for_call_by_client_ids,
    delete_waiting_offers_for_call_with_count_off_limit,
    get_client_by_avito_user_id,
    get_client_by_client_id,
    get_last_sync_date,
    get_offers_parsed_ids_by_parsed_ids,
    get_offers_regions_by_client_id,
    get_waiting_offer_counts_by_clients,
    get_waiting_offers_for_call,
    save_client,
    save_offer_for_call,
    set_synced_and_fetch_parsed_offers_chunk,
    set_waiting_offers_priority_by_offer_ids,
)
from external_offers.services.prioritizers import prioritize_homeowner_client, prioritize_smb_client
from external_offers.services.prioritizers.prioritize_offer import mapping_offer_categories_to_priority


logger = logging.getLogger(__name__)

_CLEAR_CLIENT_PRIORITY = -1
_NO_ACTIVE = 0


async def clear_waiting_offers_and_clients_with_off_count_limits() -> None:
    await gen.multi([
        delete_waiting_clients_with_count_off_limit(),
        delete_waiting_offers_for_call_with_count_off_limit()
    ])


async def clear_waiting_offers_and_clients_by_clients_ids(
    *,
    clients_ids
) -> None:
    if runtime_settings.get(
        'ENABLE_CLEAR_OLD_WAITING_OFFERS_FOR_CALL',
        settings.ENABLE_CLEAR_OLD_WAITING_OFFERS_FOR_CALL
    ):
        await delete_old_waiting_offers_for_call()
    await gen.multi([
        delete_waiting_offers_for_call_by_client_ids(
            client_ids=clients_ids
        ),
        delete_waiting_clients_by_client_ids(
            client_ids=clients_ids
        ),
    ])


async def prioritize_client(
    *,
    client_id: str,
    client_count: int,
) -> int:
    """ Возвращаем приоритет клиента, если клиента нужно убрать из очереди возвращаем _CLEAR_CLIENT_PRIORITY """

    client: Client = await get_client_by_client_id(
        client_id=client_id
    )
    regions = await get_offers_regions_by_client_id(
        client_id=client_id
    )
    if regions == []:
        return _CLEAR_CLIENT_PRIORITY

    priority = _CLEAR_CLIENT_PRIORITY

    if client and client.segment and client.segment.is_c:
        priority = await prioritize_smb_client(
            client=client,
            client_count=client_count,
            regions=regions
        )

    if client and client.segment and client.segment.is_d:
        priority = await prioritize_homeowner_client(
            client=client,
            regions=regions
        )

    return priority


async def clear_and_prioritize_waiting_offers() -> None:
    """ Очищаем таблицу заданий и клиентов и проставляем приоритеты заданиям """

    await clear_waiting_offers_and_clients_with_off_count_limits()

    clients_counts = await get_waiting_offer_counts_by_clients()

    clients_priority: Dict[int, int] = {}
    offers_priority: Dict[int, List[str]] = defaultdict(list)
    to_clear: List[str] = []

    for client_count in clients_counts:
        with new_operation_id():
            client_priority = await prioritize_client(
                client_id=client_count.client_id,
                client_count=client_count.waiting_offers_count
            )
        if client_priority == _CLEAR_CLIENT_PRIORITY:
            to_clear.append(client_count.client_id)
        else:
            clients_priority[client_count.client_id] = client_priority

    logger.warning(
        'После приоритизации %d клиентов будут удалены',
        len(to_clear)
    )

    await clear_waiting_offers_and_clients_by_clients_ids(
        clients_ids=to_clear
    )

    async with pg.get().transaction():
        async for waiting_offer_for_call in get_waiting_offers_for_call():
            category = waiting_offer_for_call.category
            client_id = waiting_offer_for_call.client_id
            offer_id = waiting_offer_for_call.id
            if clients_priority.get(client_id) is not None:
                final_priority = str(clients_priority[client_id]) + str(mapping_offer_categories_to_priority[category])
                offers_priority[int(final_priority)].append(offer_id)

    for priority, offer_ids in offers_priority.items():

        logger.warning(
            'После приоритизации для %d обьявлений будет задан приоритет %d',
            len(offer_ids),
            priority
        )

        await set_waiting_offers_priority_by_offer_ids(
            offer_ids=offer_ids,
            priority=priority
        )


async def sync_offers_for_call_with_parsed():
    """ Синхронизировать таблицу заданий offers_for_call и parsed_offers """
    last_sync_date = None
    if settings.ENABLE_LAST_SYNC_DATE_FETCHING:
        last_sync_date = await get_last_sync_date()

    while parsed_offers := await set_synced_and_fetch_parsed_offers_chunk(
        last_sync_date=last_sync_date
    ):
        logger.info('Fetched %d parsed offers', len(parsed_offers))

        rows = await get_offers_parsed_ids_by_parsed_ids(
            parsed_ids=[offer.id for offer in parsed_offers]
        )
        parsed_offer_ids_existing = set(row['parsed_id'] for row in rows)

        for parsed_offer in parsed_offers:
            if parsed_offer.id in parsed_offer_ids_existing:
                continue

            client = await get_client_by_avito_user_id(
                avito_user_id=parsed_offer.source_user_id
            )
            if client:
                if not client.status.is_waiting:
                    continue
            else:
                client_phones = json.loads(parsed_offer.phones)
                client_contact = parsed_offer.contact
                segment = parsed_offer.user_segment

                client_id = generate_guid()
                client = Client(
                    client_id=client_id,
                    avito_user_id=parsed_offer.source_user_id,
                    client_name=client_contact,
                    client_phones=client_phones if client_phones else [],
                    status=ClientStatus.waiting,
                    segment=UserSegment.from_str(segment) if segment else None
                )
                await save_client(
                    client=client
                )

            offer_id = generate_guid()
            now = datetime.now(tz=pytz.utc)
            offer = Offer(
                id=offer_id,
                parsed_id=parsed_offer.id,
                client_id=client.client_id,
                status=client.status,
                created_at=now,
                synced_at=parsed_offer.timestamp,
                parsed_created_at=parsed_offer.created_at,
                category=parsed_offer.category,
            )
            await save_offer_for_call(offer=offer)

    await clear_and_prioritize_waiting_offers()
