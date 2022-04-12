import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Optional, Union

import pytz
from cian_core.context import new_operation_id
from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_json import json
from tornado import gen

from external_offers import pg
from external_offers.entities import Offer
from external_offers.entities.client_account_statuses import ClientAccountStatus, HomeownerAccount, SmbAccount
from external_offers.entities.clients import Client, ClientDraftOffersCount, ClientStatus, ClientWaitingOffersCount
from external_offers.entities.parsed_offers import ParsedOfferForAccountPrioritization
from external_offers.entities.teams import Team
from external_offers.enums import UserSegment
from external_offers.helpers.phonenumber import transform_phone_number_to_canonical_format
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
from external_offers.repositories.postgresql.client_account_statuses import (
    get_client_account_statuses,
    get_recently_cached_client_account_statuses,
    set_client_account_status,
)
from external_offers.repositories.postgresql.clients_priorities import (
    get_clients_priority_by_team_id,
    save_clients_priority,
)
from external_offers.repositories.postgresql.offers import (
    clear_invalid_waiting_offers_by_offer_ids,
    delete_calltracking_clients,
    delete_calltracking_offers,
    get_offers_regions_by_client_ids,
    set_waiting_offers_team_priorities_by_offer_ids,
)
from external_offers.repositories.postgresql.parsed_offers import get_parsed_offers_for_account_prioritization
from external_offers.repositories.postgresql.teams import get_teams
from external_offers.services.prioritizers import (
    find_homeowner_account,
    find_smb_account,
    prioritize_homeowner_client,
    prioritize_smb_client,
)
from external_offers.services.prioritizers.prioritize_offer import get_mapping_offer_categories_to_priority
from external_offers.utils import iterate_over_list_by_chunks
from external_offers.utils.teams import get_team_info


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
    team_settings: dict[str, Union[int, str, list[str]]],
    client_account_statuses: Optional[dict[str, ClientAccountStatus]] = None,
    clients_regions: dict[str, list[int]],
) -> int:
    """ Возвращаем приоритет клиента, если клиента нужно убрать из очереди возвращаем _CLEAR_PRIORITY """

    with new_operation_id():
        client: Optional[Client] = await get_client_by_client_id(
            client_id=client_id
        )
        regions = clients_regions.get(client_id, [])

        # regions = await get_offers_regions_by_client_id(
        #     client_id=client_id
        # )

        if regions in ([], [None]):
            return _CLEAR_PRIORITY

        if client and client.segment and client.segment.is_c:
            priority = await prioritize_smb_client(
                client=client,
                client_count=client_count,
                regions=regions,
                team_settings=team_settings,
                client_account_statuses=client_account_statuses,
            )
            return priority

        if client and client.segment and client.segment.is_d:
            priority = await prioritize_homeowner_client(
                client=client,
                regions=regions,
                team_settings=team_settings,
                client_account_statuses=client_account_statuses,
            )
            return priority

        return _CLEAR_PRIORITY


async def prioritize_unactivated_clients(
    clients_priority: dict[str, Union[str, int]],
    unactivated_clients_counts: list[ClientDraftOffersCount],
    team_settings: dict[str, Union[int, str, list[str]]],
    clients_regions: dict[str, list[int]]
) -> dict[str, Union[str, int]]:
    """ Просчитать приоритеты для добивочных заданий """
    logger.info('Начало просчета приоритета для добивочных заданий')
    prefix = team_settings['unactivated_client_priority']
    prefix = str(prefix)

    total = 0
    for unactivated_clients_counts_chunk in iterate_over_list_by_chunks(
            iterable=unactivated_clients_counts,
            chunk_size=runtime_settings.CHUNK_SIZE_FOR_PRIORITY_CLIENTS,
    ):
        prioritize_client_coros = []
        for client_count in unactivated_clients_counts_chunk:
            prioritize_client_coro = prioritize_client(
                client_id=client_count.client_id,
                client_count=client_count.draft_offers_count,
                team_settings=team_settings,
                clients_regions=clients_regions,
            )
            prioritize_client_coros.append(prioritize_client_coro)

        chunk_priorities = await asyncio.gather(*prioritize_client_coros, return_exceptions=True)

        for client_count, client_priority in zip(unactivated_clients_counts_chunk, chunk_priorities):
            if not isinstance(client_priority, int):
                logger.warning(
                    'Приоритет для клиента %s не был просчитан из-за ошибки %s',
                    client_count.client_id,
                    client_priority,
                )
                continue

            if client_priority == _CLEAR_PRIORITY:
                priority = client_count.priority
                if priority is None:
                    continue
                client_priority = prefix + str(priority)[1:-2]
            else:
                client_priority = prefix + str(client_priority)
            clients_priority[client_count.client_id] = client_priority
        total += len(unactivated_clients_counts_chunk)
        logger.info('Обработано %s / %s', total, len(unactivated_clients_counts))
    logger.info('Конец просчета приоритета для добивочных заданий')
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
    raw_priority = list(priority)
    # склеивает в 1 строку 3 цифры из которых состоит приоритет региона
    old_region_priority = raw_priority[3] + raw_priority[4] + raw_priority[5]
    del raw_priority[3]
    del raw_priority[3]
    raw_priority[3] = old_region_priority

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
    activation_status_value = raw_priority[old_positions['activation_status']-1]
    call_status_value = raw_priority[old_positions['call_status']-1]
    region_value = raw_priority[old_positions['region']-1]
    segment_value = raw_priority[old_positions['segment']-1]
    lk_value = raw_priority[old_positions['lk']-1]
    deal_type_value = raw_priority[old_positions['deal_type']-1]
    offer_type_value = raw_priority[old_positions['offer_type']-1]

    # новые положения в приоритете, которые достаются из teams.settings
    new_activation_status_position = team_settings.get('activation_status_position', old_positions['activation_status'])
    new_call_status_position = team_settings.get('call_status_position', old_positions['call_status'])
    new_region_position = team_settings.get('region_position', old_positions['region'])
    new_segment_position = team_settings.get('segment_position', old_positions['segment'])
    new_lk_position = team_settings.get('lk_position', old_positions['lk'])
    new_deal_type_position = team_settings.get('deal_type_position', old_positions['deal_type'])
    new_offer_type_position = team_settings.get('offer_type_position', old_positions['offer_type'])

    # в новые положения проставляются значения
    shuffled_priority = []
    positions_amount = len(old_positions.keys())
    for _ in range(positions_amount):
        shuffled_priority.append(None)
    # -1 нужен потому что тимлиды проставляют значения позиций начиная с 1, а не с 0
    shuffled_priority[new_activation_status_position-1] = activation_status_value
    shuffled_priority[new_call_status_position-1] = call_status_value
    shuffled_priority[new_region_position-1] = region_value
    shuffled_priority[new_segment_position-1] = segment_value
    shuffled_priority[new_lk_position-1] = lk_value
    shuffled_priority[new_deal_type_position-1] = deal_type_value
    shuffled_priority[new_offer_type_position-1] = offer_type_value
    shuffled_priority = ''.join(shuffled_priority)
    return shuffled_priority


async def prioritize_clients(
    *,
    waiting_clients_counts: list[ClientWaitingOffersCount],
    team_settings: dict[str, Union[int, str, list[str]]],
    client_account_statuses: dict[str, ClientAccountStatus],
    clients_regions: dict[str, list[int]],
) -> dict[str, Union[str, int]]:
    logger.info('Начало просчета приоритета для клиентов в ожидании')
    prefix = team_settings['new_client_priority']
    prefix = str(prefix)
    clients_priority: dict[str, int] = {}

    total = 0
    for waiting_clients_counts_chunk in iterate_over_list_by_chunks(
            iterable=waiting_clients_counts,
            chunk_size=runtime_settings.CHUNK_SIZE_FOR_PRIORITY_CLIENTS,
    ):
        prioritize_client_coros = []
        for client_count in waiting_clients_counts_chunk:
            prioritize_client_coro = prioritize_client(
                client_id=client_count.client_id,
                client_count=client_count.waiting_offers_count,
                team_settings=team_settings,
                client_account_statuses=client_account_statuses,
                clients_regions=clients_regions,
            )
            prioritize_client_coros.append(prioritize_client_coro)

        chunk_priorities = await asyncio.gather(*prioritize_client_coros, return_exceptions=True)

        for client_count, client_priority in zip(waiting_clients_counts_chunk, chunk_priorities):
            if not isinstance(client_priority, int):
                logger.warning(
                    'Приоритет для клиента %s не был просчитан из-за ошибки %s',
                    client_count.client_id,
                    client_priority,
                )
                continue
            if client_priority != _CLEAR_PRIORITY:
                client_priority = prefix + str(client_priority)
            clients_priority[client_count.client_id] = client_priority
        total += len(waiting_clients_counts_chunk)
        logger.info('Обработано %s / %s', total, len(waiting_clients_counts))
    logger.info('Конец просчета приоритета для клиентов в ожидании')
    return clients_priority


async def sync_offers_for_call_with_parsed(is_test: bool) -> None:
    """ Синхронизировать таблицу заданий offers_for_call и parsed_offers """
    max_updated_at_date = None
    if runtime_settings.get('ENABLE_UPDATED_AT_DATE_FETCHING', True):
        max_updated_at_date = datetime.now(tz=pytz.utc)
    logger.warning(
        'Создание заданий и клиентов было запущено для всех обьявлений обновленных не позже %s',
        max_updated_at_date
    )
    last_sync_date = None
    if runtime_settings.ENABLE_LAST_SYNC_DATE_FETCHING:
        last_sync_date = await get_last_sync_date()
    while parsed_offers := await set_synced_and_fetch_parsed_offers_chunk(
        last_sync_date=last_sync_date,
        max_updated_at_date=max_updated_at_date,
        is_test=is_test,
    ):
        logger.warning('Fetched %d parsed offers', len(parsed_offers))

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
                    is_test=is_test,
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
                source_object_id=parsed_offer.source_object_id,
                client_id=client.client_id,
                status=client.status,
                created_at=now,
                synced_at=parsed_offer.timestamp,
                parsed_created_at=parsed_offer.created_at,
                category=parsed_offer.category,
                external_offer_type=parsed_offer.external_offer_type,
                is_test=is_test,
                is_calltracking=parsed_offer.is_calltracking,
            )
            await save_offer_for_call(offer=offer)


async def sync_and_create_offers(is_test: bool) -> None:
    logger.warning('Наполнение очереди заданиями было запущено')
    await sync_offers_for_call_with_parsed(is_test=is_test)
    logger.info('Начало процесса приоритезации')
    with statsd.timer('offers_prioritization'):
        await clear_and_prioritize_waiting_offers(is_test=is_test)
    logger.info('Конец процесса приоритезации')


async def clear_and_prioritize_waiting_offers(is_test: bool) -> None:
    logger.warning('Очистка и приоретизация заданий была запущена')
    await clear_waiting_offers_and_clients_with_off_count_limits()

    # None нужен для того чтобы проставить некомандные приоритеты
    teams = [None, ]
    if runtime_settings.ENABLE_TEAMS_PRIORITIZATION:
        teams.extend(await get_teams())
    await prioritize_waiting_offers(
        teams=teams,
        is_test=is_test,
    )

    if runtime_settings.EXCLUDE_CALLTRACKING_FOR_ALL_TEAMS:
        await delete_calltracking_clients()
        await delete_calltracking_offers()

    if runtime_settings.ENABLE_CLEAR_OLD_WAITING_OFFERS_FOR_CALL:
        await delete_old_waiting_offers_for_call()


async def create_priorities(
    *,
    waiting_clients_counts: list[Optional[ClientWaitingOffersCount]],
    unactivated_clients_counts: list[Optional[ClientDraftOffersCount]],
    team_settings: dict,
    team_id: Optional[int] = None,
    client_account_statuses: dict[str, ClientAccountStatus],
    clients_regions: dict[str, list[int]]
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

    if runtime_settings.get('USE_CACHED_CLIENTS_PRIORITY', False):
        clients_priority = await get_cached_clients_priority(
            waiting_clients_counts=waiting_clients_counts,
            team_settings=team_settings,
            client_account_statuses=client_account_statuses,
            team_id=team_id,
            clients_regions=clients_regions,
        )
    else:
        # создает часть приоритета для клиентов в ожидании
        clients_priority = await prioritize_clients(
            waiting_clients_counts=waiting_clients_counts,
            team_settings=team_settings,
            client_account_statuses=client_account_statuses,
            clients_regions=clients_regions,
        )
    # создает часть приоритета для добивочных клиентов
    clients_priority = await prioritize_unactivated_clients(
        clients_priority=clients_priority,
        unactivated_clients_counts=unactivated_clients_counts,
        team_settings=team_settings,
        clients_regions=clients_regions,
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


async def get_cached_clients_priority(
    *,
    waiting_clients_counts: list[Optional[ClientWaitingOffersCount]],
    team_settings: dict,
    client_account_statuses: dict[str, ClientAccountStatus],
    team_id: Optional[int] = None,
    clients_regions: dict[str, list[int]],
) -> dict[str, str]:
    # достает закешированную часть приоритета для клиентов в ожидании
    clients_priority = await get_clients_priority_by_team_id(team_id)
    if not clients_priority:
        # создает часть приоритета для клиентов в ожидании
        clients_priority = await prioritize_clients(
            waiting_clients_counts=waiting_clients_counts,
            team_settings=team_settings,
            client_account_statuses=client_account_statuses,
            clients_regions=clients_regions,
        )
        # кеширует часть приоритета для клиентов в ожидании
        await save_clients_priority(
            clients_priority=clients_priority,
            team_id=team_id,
        )
    return clients_priority


async def prioritize_waiting_offers(
    *,
    teams: list[Optional[Team]],
    is_test: bool,
) -> None:
    logger.warning('Приоретизация заданий была запущена')
    created_offers_priorities = []
    client_account_statuses = {}
    clients_regions = await get_offers_regions_by_client_ids()
    logger.warning('Количество закешированых регионов клиентов: %s', len(clients_regions))

    if runtime_settings.get('USE_CACHED_CLIENT_ACCOUNT_STATUSES', True):
        client_account_statuses: dict[str, ClientAccountStatus] = await get_client_account_statuses()
    logger.warning('Количество закешированых статусов клиентов: %s', len(client_account_statuses))

    for team in teams:

        team_info = get_team_info(team)
        team_id = team_info.team_id
        logger.warning('Приоретизация заданий для команды %s была запущена', team_id)

        unactivated_clients_counts = await get_unactivated_clients_counts_by_clients(
            is_test=is_test,
        )
        logger.warning('Количество добивочных заданий для приоретизации: %s', len(unactivated_clients_counts))

        waiting_clients_counts = await get_waiting_offer_counts_by_clients(
            team_settings=team_info.team_settings,
            is_test=is_test,
            team_id=team_id,
        )

        logger.warning(
            'Количество заданий в ожидании для приоретизации для команды %s: %s',
            team_id,
            len(waiting_clients_counts),
        )
        created_offers_priorities.append(
            create_priorities(
                waiting_clients_counts=waiting_clients_counts,
                unactivated_clients_counts=unactivated_clients_counts,
                team_settings=team_info.team_settings,
                team_id=team_id,
                client_account_statuses=client_account_statuses,
                clients_regions=clients_regions,
            )
        )

        # cleared_offer_ids = await clear_invalid_waiting_offers_by_offer_ids(
        #     team_id=team_id,
        #     is_test=is_test,
        #     team_settings=team_settings,
        # )
        # logger.warning(
        #     'Количество заданий в ожидании для очистки для команды %s: %s ',
        #     team_id,
        #     len(cleared_offer_ids),
        # )

    offers_priority_for_teams = await asyncio.gather(*created_offers_priorities)
    for offers_priority_for_team in offers_priority_for_teams:
        team_id = offers_priority_for_team['team_id']
        offers_priority = offers_priority_for_team['offers_priority']
        if team_id:
            for priority, offer_ids in offers_priority.items():
                logger.warning(
                    'После приоритизации для команды %d для %d обьявлений будет задан приоритет %d',
                    team_id,
                    len(offer_ids),
                    priority
                )
                await set_waiting_offers_team_priorities_by_offer_ids(
                    offer_ids=offer_ids,
                    priority=priority,
                    team_id=team_id
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

    for team in teams:
        team_info = get_team_info(team)
        logger.warning('Очистка заданий для команды %s была запущена', team_id)
        cleared_offer_ids = await clear_invalid_waiting_offers_by_offer_ids(
            team_id=team_info.team_id,
            is_test=is_test,
            team_settings=team_info.team_settings,
            team_type=team_info.team_type,
        )
        logger.warning(
            'Количество заданий в ожидании для очистки для команды %s: %s ',
            team_id,
            len(cleared_offer_ids),
        )


async def create_client_account_statuses() -> None:
    if not runtime_settings.get('ENABLE_CLIENT_ACCOUNT_STATUSES_CASHING', True):
        logger.warning('Кеширование приоритетов по ЛК клиентов отключено')
        return False
    parsed_offers = await get_parsed_offers_for_account_prioritization()
    recently_cached_client_account_statuses = await get_recently_cached_client_account_statuses()
    logger.warning(
        'Кеширование приоритетов по ЛК для %s обьявлений запущено.',
        len(parsed_offers),
    )
    # достает все спаршеные обьявления, кроме тех, по номерам телефонов которых были обновления за последние 5 дней
    for parsed_offer in parsed_offers:
        parsed_offer: ParsedOfferForAccountPrioritization

        phone = json.loads(parsed_offer.phones)[0]
        if phone in recently_cached_client_account_statuses:
            continue

        canonical_phone = transform_phone_number_to_canonical_format(phone)
        if canonical_phone in recently_cached_client_account_statuses:
            continue

        now = datetime.now(tz=pytz.UTC)
        with new_operation_id():
            if parsed_offer.user_segment == UserSegment.c.value:
                account: SmbAccount = await find_smb_account(phone=phone)
                await set_client_account_status({
                    'created_at': now,
                    'updated_at': now,
                    'phone': phone,
                    'smb_account_status': getattr(account.account_status, 'value', None),
                    'homeowner_account_status': None,
                    'new_cian_user_id': account.new_cian_user_id,
                })
            elif parsed_offer.user_segment == UserSegment.d.value:
                account: HomeownerAccount = await find_homeowner_account(phone=phone)
                await set_client_account_status({
                    'created_at': now,
                    'updated_at': now,
                    'phone': phone,
                    'smb_account_status': None,
                    'homeowner_account_status': account.account_status.value,
                    'new_cian_user_id': account.new_cian_user_id,
                })
