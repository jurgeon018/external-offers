import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional

import pytz
from cian_core.context import new_operation_id
from cian_core.runtime_settings import runtime_settings
from cian_json import json
from tornado import gen

from external_offers import pg
from external_offers.entities import Offer
from external_offers.entities.clients import Client, ClientDraftOffersCount, ClientStatus, ClientWaitingOffersCount
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
    delete_calltracking_clients,
    delete_calltracking_offers,
    set_waiting_offers_team_priorities_by_offer_ids,
)
from external_offers.repositories.postgresql.teams import get_teams
from external_offers.services.prioritizers import prioritize_homeowner_client, prioritize_smb_client
from external_offers.services.prioritizers.prioritize_offer import get_mapping_offer_categories_to_priority


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
    team_settings: dict,
) -> int:
    """ Возвращаем приоритет клиента, если клиента нужно убрать из очереди возвращаем _CLEAR_PRIORITY """

    client: Optional[Client] = await get_client_by_client_id(
        client_id=client_id
    )
    regions = await get_offers_regions_by_client_id(
        client_id=client_id
    )

    if regions in ([], [None]):
        return _CLEAR_PRIORITY

    if client and client.segment and client.segment.is_c:
        priority = await prioritize_smb_client(
            client=client,
            client_count=client_count,
            regions=regions,
            team_settings=team_settings,
        )
        return priority

    if client and client.segment and client.segment.is_d:
        priority = await prioritize_homeowner_client(
            client=client,
            regions=regions,
            team_settings=team_settings,
        )
        return priority

    return _CLEAR_PRIORITY


async def prioritize_unactivated_clients(
    clients_priority: list[ClientWaitingOffersCount],
    unactivated_clients_counts: list[ClientDraftOffersCount],
    team_settings: dict,
    team: Optional[Team] = None,
) -> list[ClientWaitingOffersCount]:
    """ Просчитать приоритеты для добивочных заданий """

    prefix = team_settings.get(
        'unactivated_client_priority',
        runtime_settings.UNACTIVATED_CLIENT_PRIORITY
    )
    prefix = str(prefix)

    for client_count in unactivated_clients_counts:
        with new_operation_id():
            client_priority = await prioritize_client(
                client_id=client_count.client_id,
                client_count=client_count.draft_offers_count,
                team_settings=team_settings,
            )
        if client_priority == _CLEAR_PRIORITY:
            if team:
                team_priorities = {}
                if client_count.team_priorities:
                    team_priorities = json.loads(client_count.team_priorities)
                priority = team_priorities.get(str(team.team_id))
            else:
                priority = client_count.priority
            if priority is None:
                continue
            client_priority = prefix + str(priority)[1:-2]
        else:
            client_priority = prefix + str(client_priority)
        clients_priority[client_count.client_id] = client_priority
    return clients_priority


async def prioritize_offers(
    clients_priority: dict,
    team_settings: dict,
):
    offers_priority: dict[int, list[str]] = defaultdict(list)

    async with pg.get().transaction():
        async for offer in get_offers_for_prioritization_by_client_ids(clients_priority.keys()):
            client_priority = clients_priority[offer.client_id]
            if int(client_priority) == _CLEAR_PRIORITY:
                final_priority = str(_CLEAR_PRIORITY)
            else:
                mapping_offer_categories_to_priority = get_mapping_offer_categories_to_priority(
                    team_settings=team_settings,
                )
                offer_priority = mapping_offer_categories_to_priority[offer.category]
                final_priority = str(client_priority) + str(offer_priority)
                if len(final_priority) == 9:
                    final_priority = shuffle_priority_positions(
                        priority=final_priority,
                        team_settings=team_settings,
                    )
            offers_priority[int(final_priority)].append(offer.id)
    return offers_priority


def shuffle_priority_positions(
    priority: str,
    team_settings: dict,
) -> str:
    old_priority = list(priority)
    # склеивает в 1 строку 3 цифры из которых состоит приоритет региона
    old_region_priority = old_priority[3] + old_priority[4] + old_priority[5]
    del old_priority[3]
    del old_priority[3]
    old_priority[3] = old_region_priority

    # дефолтные положения в приоритете, который получился после приоритизации
    old_positions = {
        'activation_status': 1,
        'call_status': 2,
        'region': 3,
        'segment': 4,
        'lk': 5,
        'deal_type': 6,
        'offer_type': 7,
    }

    # значения в приоритете который получился после приоретизации
    activation_status_value = old_priority[old_positions['activation_status']-1]
    call_status_value = old_priority[old_positions['call_status']-1]
    region_value = old_priority[old_positions['region']-1]
    segment_value = old_priority[old_positions['segment']-1]
    lk_value = old_priority[old_positions['lk']-1]
    deal_type_value = old_priority[old_positions['deal_type']-1]
    offer_type_value = old_priority[old_positions['offer_type']-1]

    # новые положения в приоритете, которые достаются из teams.settings
    new_activation_status_position = team_settings.get('activation_status_position', old_positions['activation_status'])
    new_call_status_position = team_settings.get('call_status_position', old_positions['call_status'])
    new_region_position = team_settings.get('region_position', old_positions['region'])
    new_segment_position = team_settings.get('segment_position', old_positions['segment'])
    new_lk_position = team_settings.get('lk_position', old_positions['lk'])
    new_deal_type_position = team_settings.get('deal_type_position', old_positions['deal_type'])
    new_offer_type_position = team_settings.get('offer_type_position', old_positions['offer_type'])

    # в новые положения проставляются значения
    new_priority = []
    positions_amount = len(old_positions.keys())
    for _ in range(positions_amount):
        new_priority.append(None)
    new_priority[new_activation_status_position-1] = activation_status_value
    new_priority[new_call_status_position-1] = call_status_value
    new_priority[new_region_position-1] = region_value
    new_priority[new_segment_position-1] = segment_value
    new_priority[new_lk_position-1] = lk_value
    new_priority[new_deal_type_position-1] = deal_type_value
    new_priority[new_offer_type_position-1] = offer_type_value
    new_priority = ''.join(new_priority)
    return new_priority


async def prioritize_clients(
    *,
    waiting_clients_counts: list[ClientWaitingOffersCount],
    team_settings: dict,
):
    prefix = team_settings.get(
        'new_client_priority',
        runtime_settings.NEW_CLIENT_PRIORITY
    )
    prefix = str(prefix)
    clients_priority: dict[int, int] = {}
    for client_count in waiting_clients_counts:
        with new_operation_id():
            client_priority = await prioritize_client(
                client_id=client_count.client_id,
                client_count=client_count.waiting_offers_count,
                team_settings=team_settings,
            )
        if client_priority != _CLEAR_PRIORITY:
            client_priority = prefix + str(client_priority)
        clients_priority[client_count.client_id] = client_priority
    return clients_priority


async def sync_offers_for_call_with_parsed() -> None:
    """ Синхронизировать таблицу заданий offers_for_call и parsed_offers """
    last_sync_date = None
    if runtime_settings.ENABLE_LAST_SYNC_DATE_FETCHING:
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
                    segment=UserSegment.from_str(segment) if segment else None,
                    subsegment=parsed_offer.user_subsegment,
                )
                await save_client(
                    client=client
                )

            offer_id = generate_guid()
            now = datetime.now(tz=pytz.utc)
            offer = Offer(
                id=offer_id,
                group_id=parsed_offer.source_group_id,
                parsed_id=parsed_offer.id,
                client_id=client.client_id,
                status=client.status,
                created_at=now,
                synced_at=parsed_offer.timestamp,
                parsed_created_at=parsed_offer.created_at,
                category=parsed_offer.category,
                external_offer_type=parsed_offer.external_offer_type,
            )
            await save_offer_for_call(offer=offer)
    await clear_and_prioritize_waiting_offers()


async def clear_and_prioritize_waiting_offers():
    await clear_waiting_offers_and_clients_with_off_count_limits()

    # None нужен для того чтобы проставить некомандные приоритеты
    teams = [None, ]
    if runtime_settings.get('ENABLE_TEAMS_PRIORITIZATION', False):
        teams.extend(await get_teams())
    await prioritize_waiting_offers(teams=teams)

    await delete_calltracking_clients()

    await delete_calltracking_offers()

    if runtime_settings.ENABLE_CLEAR_OLD_WAITING_OFFERS_FOR_CALL:
        await delete_old_waiting_offers_for_call()


async def prioritize_waiting_offers(
    *,
    teams: list[Optional[Team]],
    is_test: bool = None,
):

    client_counts_for_prioritization = []
    for team in teams:

        if team:
            team_settings = team.get_settings()
        else:
            team_settings = {}

        # достает спаршеные обьявления с невалидными для текущих настроек полями(категория, сегмент, регион)
        # и связаным с обьявлениями заданиям проставляет _CLEAR_PRIORITY, чтобы задания не выдавались
        # (задания фильтруются в assign_suitable_client_to_operator по приоритету _CLEAR_PRIORITY)
        waiting_clients_counts, unactivated_clients_counts = await asyncio.gather(
            # достает задания в ожидании(фильтрует задания которыми выше был проставлен приоритет _CLEAR_PRIORITY)
            get_waiting_offer_counts_by_clients(team=team, is_test=is_test),
            # достает добивочные задания
            get_unactivated_clients_counts_by_clients(),
        )
        client_counts_for_prioritization.append(
            create_priorities(
                waiting_clients_counts=waiting_clients_counts,
                unactivated_clients_counts=unactivated_clients_counts,
                team_settings=team_settings,
                team_id=team.team_id,
            )
        )

    created_priorities = await asyncio.gather(*client_counts_for_prioritization)

    for created_priority in created_priorities:
        team = created_priority['team_id']
        offers_priority = created_priority['offers_priority']
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


async def create_priorities(
    *,
    waiting_clients_counts,
    unactivated_clients_counts,
    team_settings: dict,
    team_id: Optional[int] = None,
) -> dict[int, dict[int, list[str]]]:
    if team_id:
        logger.warning(
            'Приоретизация для команды %s для %d клиентов в ожидании запущена.',
            team_id,
            len(waiting_clients_counts),
        )
        logger.warning(
            'Приоретизация для команды %s для %d добивочных клиентов запущена.',
            team_id,
            len(unactivated_clients_counts),
        )
    else:
        logger.warning(
            'Приоретизация для %d клиентов в ожидании запущена.',
            len(waiting_clients_counts),
        )
        logger.warning(
            'Приоретизация для %d добивочных клиентов запущена.',
            len(unactivated_clients_counts),
        )

    # создает часть приоритета для клиентов в ожидании
    clients_priority = await prioritize_clients(
        waiting_clients_counts=waiting_clients_counts,
        team_settings=team_settings,
    )
    # создает часть приоритета для добивочных клиентов
    clients_priority = await prioritize_unactivated_clients(
        clients_priority=clients_priority,
        unactivated_clients_counts=unactivated_clients_counts,
        team_settings=team_settings,
    )
    # создает часть приоритета для заданий + склеивает с приоритетами клиентов
    offers_priority = await prioritize_offers(
        clients_priority=clients_priority,
        team_settings=team_settings,
    )
    return {
        'team_id': team_id,
        'offers_priority': offers_priority,
    }
