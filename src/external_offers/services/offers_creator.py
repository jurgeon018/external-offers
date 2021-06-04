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

from external_offers.entities import Offer
from external_offers.entities.clients import Client, ClientStatus
from external_offers.enums import UserSegment
from external_offers.enums.object_model import Category
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
    save_client,
    save_offer_for_call,
    set_synced_and_fetch_parsed_offers_chunk,
    set_waiting_offers_priority_by_offer_ids,
    get_waiting_offers_for_call_by_client_id,
    get_waiting_offers_for_call,
)
from external_offers.services.prioritizers import prioritize_homeowner_client, prioritize_smb_client


logger = logging.getLogger(__name__)

_CLEAR_CLIENT_PRIORITY = -1
_NO_ACTIVE = 0
SALE_PRIORITY = str(runtime_settings.SALE_PRIORITY)
RENT_PRIORITY = str(runtime_settings.RENT_PRIORITY)
FLAT_PRIORITY = str(runtime_settings.FLAT_PRIORITY)
SUBURBAN_PRIORITY = str(runtime_settings.SUBURBAN_PRIORITY)
COMMERCIAL_PRIORITY = str(runtime_settings.COMMERCIAL_PRIORITY)


mapping_offer_categories_to_priority = {
    Category.bed_rent: RENT_PRIORITY + FLAT_PRIORITY,
    Category.building_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.building_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
    Category.business_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.business_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
    Category.car_service_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.car_service_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
    Category.commercial_land_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.commercial_land_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
    Category.cottage_rent: RENT_PRIORITY + SUBURBAN_PRIORITY,
    Category.cottage_sale: SALE_PRIORITY + SUBURBAN_PRIORITY,
    Category.daily_bed_rent: RENT_PRIORITY + FLAT_PRIORITY,
    Category.daily_flat_rent: RENT_PRIORITY + FLAT_PRIORITY,
    Category.daily_house_rent: RENT_PRIORITY + FLAT_PRIORITY,
    Category.daily_room_rent: RENT_PRIORITY + FLAT_PRIORITY,
    Category.domestic_services_rent: RENT_PRIORITY + FLAT_PRIORITY,
    Category.domestic_services_sale: SALE_PRIORITY + FLAT_PRIORITY,
    Category.flat_rent: RENT_PRIORITY + FLAT_PRIORITY,
    Category.flat_sale: SALE_PRIORITY + FLAT_PRIORITY,
    Category.flat_share_sale: SALE_PRIORITY + FLAT_PRIORITY,
    Category.free_appointment_object_rent: RENT_PRIORITY + FLAT_PRIORITY,
    Category.free_appointment_object_sale: SALE_PRIORITY + FLAT_PRIORITY,
    Category.garage_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.garage_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
    Category.house_rent: RENT_PRIORITY + SUBURBAN_PRIORITY,
    Category.house_sale: SALE_PRIORITY + SUBURBAN_PRIORITY,
    Category.house_share_rent: RENT_PRIORITY + SUBURBAN_PRIORITY,
    Category.house_share_sale: SALE_PRIORITY + SUBURBAN_PRIORITY,
    Category.industry_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.industry_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
    Category.land_sale: SALE_PRIORITY + SUBURBAN_PRIORITY,
    Category.new_building_flat_sale: SALE_PRIORITY + FLAT_PRIORITY,
    Category.office_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.office_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
    Category.public_catering_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.public_catering_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
    Category.room_rent: RENT_PRIORITY + FLAT_PRIORITY,
    Category.room_sale: SALE_PRIORITY + FLAT_PRIORITY,
    Category.shopping_area_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.shopping_area_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
    Category.townhouse_rent: RENT_PRIORITY + SUBURBAN_PRIORITY,
    Category.townhouse_sale: SALE_PRIORITY + SUBURBAN_PRIORITY,
    Category.warehouse_rent: RENT_PRIORITY + COMMERCIAL_PRIORITY,
    Category.warehouse_sale: SALE_PRIORITY + COMMERCIAL_PRIORITY,
}


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
        )
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

    clients_priority: Dict[int, List[str]] = defaultdict(list)
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

    waiting_offers_for_call = await get_waiting_offers_for_call()
    for waiting_offer_for_call in waiting_offers_for_call:
        category = waiting_offer_for_call.category
        client_id = waiting_offer_for_call.client_id
        client_priority = clients_priority[client_id]
        offer_priority = mapping_offer_categories_to_priority[category]
        final_priority = str(client_priority) + str(offer_priority)
        offers_priority[final_priority] += waiting_offer_for_call.id

    for final_priority, offer_ids in offers_priority.items():

        logger.warning(
            'После приоритизации для %d обьявлений будет задан приоритет %d',
            len(offer_ids),
            final_priority
        )

        await set_waiting_offers_priority_by_offer_ids(
            offer_ids=offer_ids,
            priority=final_priority
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
                if client.status.is_declined or client.status.is_accepted:
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
