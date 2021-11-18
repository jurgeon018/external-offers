import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

import pytz
from cian_core.context import new_operation_id
from cian_core.runtime_settings import runtime_settings
from cian_json import json
from simple_settings import settings
from tornado import gen

from external_offers import pg
from external_offers.entities import Offer
from external_offers.entities.clients import Client, ClientStatus, ClientWaitingOffersCount
from external_offers.entities.offers import ExternalOfferType
from external_offers.entities.teams import Team
from external_offers.enums import UserSegment
from external_offers.helpers.uuid import generate_guid
from external_offers.repositories.postgresql import (
    delete_old_waiting_offers_for_call,
    delete_waiting_clients_with_count_off_limit,
    delete_waiting_offers_for_call_with_count_off_limit,
    get_client_by_avito_user_id,
    get_client_by_client_id,
    get_last_sync_date,
    get_offers_for_prioritization_by_client_ids,
    get_offers_parsed_ids_by_parsed_ids,
    get_offers_regions_by_client_id,
    get_unactivated_clients_counts_by_clients,
    get_waiting_offer_counts_by_clients,
    save_client,
    save_offer_for_call,
    set_synced_and_fetch_parsed_offers_chunk,
    set_waiting_offers_priority_by_offer_ids,
)
from external_offers.repositories.postgresql.offers import (
    set_waiting_offers_priority_by_parsed_ids,
    set_waiting_offers_team_priorities_by_offer_ids,
)
from external_offers.repositories.postgresql.parsed_offers import get_parsed_ids_for_cleaning
from external_offers.repositories.postgresql.teams import get_teams
from external_offers.services.prioritizers import prioritize_homeowner_client, prioritize_smb_client
from external_offers.services.prioritizers.prioritize_offer import mapping_offer_categories_to_priority


logger = logging.getLogger(__name__)

_CLEAR_PRIORITY = -1


async def clear_waiting_offers_and_clients_with_off_count_limits() -> None:
    """
        Очищаем таблицу заданий и клиентов.
        Удаляются те клиенты в ожидании, у которых например меньше 1 и больше 5 обьявлений.
    """

    await gen.multi([
        delete_waiting_clients_with_count_off_limit(),
        delete_waiting_offers_for_call_with_count_off_limit()
    ])


async def prioritize_client(
    *,
    client_id: str,
    client_count: int,
    team: Optional[Team],
) -> int:
    """ Возвращаем приоритет клиента, если клиента нужно убрать из очереди возвращаем _CLEAR_PRIORITY """

    if team:
        team_settings = team.get_settings()
    else:
        team_settings = None

    client: Optional[Client] = await get_client_by_client_id(
        client_id=client_id
    )
    regions = await get_offers_regions_by_client_id(
        client_id=client_id
    )

    if regions in ([], [None]):
        return _CLEAR_PRIORITY
    print('\n client: ', client)
    print('\n client and client.segment and client.segment.is_c: ', client and client.segment and client.segment.is_c)
    print('\n client and client.segment and client.segment.is_d: ', client and client.segment and client.segment.is_d)
    if client and client.segment and client.segment.is_c:
        print('SEGMENT C!!!')
        priority = await prioritize_smb_client(
            client=client,
            client_count=client_count,
            regions=regions,
            team_settings=team_settings,
        )
        return priority

    if client and client.segment and client.segment.is_d:
        print('SEGMENT D!!!')
        priority = await prioritize_homeowner_client(
            client=client,
            regions=regions,
            team_settings=team_settings,
        )
        return priority

    return _CLEAR_PRIORITY


async def prioritize_waiting_offers(
    *,
    team: Optional[Team],
) -> None:
    """Проставляем заданиям командные(team_priorities) и внекомандные(priority) приоритеты"""

    # достает спаршеные обьявления с невалидными для текущих настроек полями(категория, сегмент, регион)
    parsed_ids = await get_parsed_ids_for_cleaning(team)
    # связаным с обьявлениями заданиям проставляет _CLEAR_PRIORITY, чтобы задания не выдавались
    # (задания фильтруются в assign_suitable_client_to_operator по приоритету _CLEAR_PRIORITY)
    cleared_offer_ids = await set_waiting_offers_priority_by_parsed_ids(
        parsed_ids=parsed_ids,
        team=team,
        priority=_CLEAR_PRIORITY,
    )
    # достает задания в ожидании(при этом фильтрует задания которыми выше был проставлен приоритет _CLEAR_PRIORITY)
    waiting_clients_counts = await get_waiting_offer_counts_by_clients(
        cleared_offer_ids=cleared_offer_ids
    )
    # создает приоритеты для заданий в ожидании
    clients_priority = await prioritize_clients(
        waiting_clients_counts=waiting_clients_counts,
        team=team,
    )
    # достает добивочные задания
    unactivated_clients_counts = await get_unactivated_clients_counts_by_clients()
    # создает часть приоритета для добивочных заданий
    clients_priority = await prioritize_unactivated_clients(
        clients_priority=clients_priority,
        unactivated_clients_counts=unactivated_clients_counts,
        team=team,
    )
    # создает приоритеты для заданий + склеивает с приоритетами заданий
    offers_priority = await prioritize_offers(
        clients_priority=clients_priority,
    )
    # проставляет приоритеты заданиям
    if team:
        for priority, offer_ids in offers_priority.items():
            logger.warning(
                'После приоритизации для команды %d для %d обьявлений будет задан приоритет %d',
                team.team_id,
                len(offer_ids),
                priority
            )
            await set_waiting_offers_team_priorities_by_offer_ids(
                offer_ids=offer_ids,
                priority=priority,
                team_id=team.team_id
            )
    else:
        for priority, offer_ids in offers_priority.items():
            logger.warning(
                'После приоритизации для %d обьявлений будет задан приоритет %d',
                len(offer_ids),
                priority
            )
            await set_waiting_offers_priority_by_offer_ids(
                offer_ids=offer_ids,
                priority=priority,
            )


async def prioritize_unactivated_clients(
    clients_priority: list[ClientWaitingOffersCount],
    unactivated_clients_counts: list,
    team: Optional[Team],
) -> list[ClientWaitingOffersCount]:
    """ Просчитать приоритеты для добивочных заданий """
    prefix = str(runtime_settings.UNACTIVATED_CLIENT_PRIORITY)

    for client_count in unactivated_clients_counts:
        with new_operation_id():
            client_priority = await prioritize_client(
                client_id=client_count.client_id,
                client_count=client_count.draft_offers_count,
                team=team,
            )
        if client_priority == _CLEAR_PRIORITY:
            if client_count.priority is None:
                continue
            client_priority = prefix + str(client_count.priority)[1:-2]
        else:
            client_priority = prefix + str(client_priority)
        clients_priority[client_count.client_id] = client_priority
    return clients_priority


async def prioritize_offers(clients_priority):
    offers_priority: Dict[int, List[str]] = defaultdict(list)
    async with pg.get().transaction():
        async for offer in get_offers_for_prioritization_by_client_ids(clients_priority.keys()):
            client_priority = clients_priority[offer.client_id]
            if int(client_priority) == _CLEAR_PRIORITY:
                final_priority = str(_CLEAR_PRIORITY)
            else:
                offer_priority = mapping_offer_categories_to_priority[offer.category]
                final_priority = str(client_priority) + str(offer_priority)
            offers_priority[int(final_priority)].append(offer.id)
    return offers_priority


async def prioritize_clients(
    *,
    waiting_clients_counts: list[ClientWaitingOffersCount],
    team: Optional[Team],
):
    clients_priority: Dict[int, int] = {}
    for client_count in waiting_clients_counts:
        with new_operation_id():
            client_priority = await prioritize_client(
                client_id=client_count.client_id,
                client_count=client_count.waiting_offers_count,
                team=team,
            )
        if client_priority != _CLEAR_PRIORITY:
            prefix = str(runtime_settings.NEW_CLIENT_PRIORITY)
            client_priority = prefix + str(client_priority)
        clients_priority[client_count.client_id] = client_priority
    return clients_priority


async def sync_offers_for_call_with_parsed() -> None:
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
            print()
            print()
            print()
            print()
            if parsed_offer.id in parsed_offer_ids_existing:
                continue
            print('\n parsed_offer while creation: ', parsed_offer)
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
                print('\n client while creation: ', client)
                await save_client(
                    client=client
                )

            offer_id = generate_guid()
            now = datetime.now(tz=pytz.utc)
            external_offer_type = parsed_offer.external_offer_type
            offer = Offer(
                id=offer_id,
                parsed_id=parsed_offer.id,
                client_id=client.client_id,
                status=client.status,
                created_at=now,
                synced_at=parsed_offer.timestamp,
                parsed_created_at=parsed_offer.created_at,
                category=parsed_offer.category,
                external_offer_type=ExternalOfferType.from_str(external_offer_type) if external_offer_type else None,
            )
            await save_offer_for_call(offer=offer)
            print()
            print()
            print()
            print()
    await clear_and_prioritize_waiting_offers()


async def clear_and_prioritize_waiting_offers():
    # x = await get_waiting_offer_counts_by_clients()
    await clear_waiting_offers_and_clients_with_off_count_limits()
    # y = await get_waiting_offer_counts_by_clients()
    # print("\n x: ", x)
    # print("\n y: ", y)
    await prioritize_waiting_offers(team=None)
    teams = await get_teams()
    for team in teams:
        await prioritize_waiting_offers(team=team)

    if runtime_settings.get(
        'ENABLE_CLEAR_OLD_WAITING_OFFERS_FOR_CALL',
        runtime_settings.ENABLE_CLEAR_OLD_WAITING_OFFERS_FOR_CALL
    ):
        await delete_old_waiting_offers_for_call()
