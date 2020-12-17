import logging
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

import pytz
from cian_core.context import new_operation_id
from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException
from cian_json import json
from simple_settings import settings
from tornado import gen

from external_offers.entities import Offer
from external_offers.entities.clients import Client, ClientStatus
from external_offers.helpers.phonenumber import transform_phone_number_to_canonical_format
from external_offers.repositories.announcements import v2_get_user_active_announcements_count
from external_offers.repositories.announcements.entities import V2GetUserActiveAnnouncementsCount
from external_offers.repositories.postgresql import (
    delete_waiting_clients_by_client_ids,
    delete_waiting_clients_with_count_off_limit,
    delete_waiting_offers_for_call_by_client_ids,
    delete_waiting_offers_for_call_with_count_off_limit,
    get_client_by_avito_user_id,
    get_client_by_client_id,
    get_last_sync_date,
    get_offers_parsed_ids_by_parsed_ids,
    get_waiting_offer_counts_by_clients,
    save_client,
    save_offer_for_call,
    set_cian_user_id_by_client_id,
    set_synced_and_fetch_parsed_offers_chunk,
    set_waiting_offers_priority_by_client_ids,
)
from external_offers.repositories.users import v2_get_users_by_phone
from external_offers.repositories.users.entities import UserModelV2, V2GetUsersByPhone


logger = logging.getLogger(__name__)

_CLEAR_CLIENT_PRIORITY = -1
_NO_ACTIVE = 0

_METRIC_PRIORITIZE_FAILED = 'prioritize_client.failed'
_METRIC_PRIORITIZE_NO_LK = 'prioritize_client.no_lk'
_METRIC_PRIORITIZE_NO_ACTIVE = 'prioritize_client.no_active'
_METRIC_PRIORITIZE_KEEP_PROPORTION = 'prioritize_client.keep_proportion'


def choose_main_client_profile(user_profiles: List[UserModelV2]) -> Optional[UserModelV2]:
    """ Ищем активный профиль агента, не ЕМЛС и не саб """

    for profile in user_profiles:
        source_user_type = profile.external_user_source_type
        is_emls_or_subagent = source_user_type and (source_user_type.is_emls or source_user_type.is_sub_agents)
        if (
            profile.is_agent
            and profile.state.is_active
            and not is_emls_or_subagent
        ):
            return profile

    return None


async def prioritize_client(
    client_id: str,
    client_count: int
) -> int:
    """ Возвращаем приоритет клиента, если клиента нужно убрать из очереди возвращаем _CLEAR_CLIENT_PRIORITY """

    client: Client = await get_client_by_client_id(
        client_id=client_id
    )
    client_info = None
    cian_user_id = client.cian_user_id

    if not cian_user_id:
        phone = transform_phone_number_to_canonical_format(client.client_phones[0])

        try:
            response = await v2_get_users_by_phone(
                V2GetUsersByPhone(
                    phone=phone
                )
            )

            # Приоритет для незарегистрированных пользователей
            if not response.users:
                statsd.incr(_METRIC_PRIORITIZE_NO_LK)
                return settings.NO_LK_PRIORITY

            # Выбираем основной активный профиль пользователя
            client_info = choose_main_client_profile(response.users)
            if not client_info:
                return _CLEAR_CLIENT_PRIORITY

            cian_user_id = client_info.cian_user_id

            # Обновляем идентификатор клиента
            await set_cian_user_id_by_client_id(
                cian_user_id=client_info.cian_user_id,
                client_id=client_id
            )
        except ApiClientException as exc:
            logger.warning(
                'Ошибка при получении идентификатора клиента %s для приоритизации: %s',
                client_id,
                exc.message
            )
            statsd.incr(_METRIC_PRIORITIZE_FAILED)
            return settings.FAILED_PRIORITY

    # Получаем количество активных объявлений
    try:
        active_response = await v2_get_user_active_announcements_count(
            V2GetUserActiveAnnouncementsCount(
                user_id=cian_user_id
            )
        )
    except ApiClientException as exc:
        logger.warning(
            'Ошибка при получении количества активных объявлений клиента %s для приоритизации: %s',
            client_id,
            exc.message
        )
        statsd.incr(_METRIC_PRIORITIZE_FAILED)
        return settings.FAILED_PRIORITY

    # Приоритет по отсутствию активных объявлений на циане
    if active_response.count == _NO_ACTIVE:
        statsd.incr(_METRIC_PRIORITIZE_NO_ACTIVE)
        return settings.NO_ACTIVE_PRIORITY

    # Приоритет по доле активных объявлений на циане к спаршенным с других площадок
    if (active_response.count / client_count) <= settings.MAXIMUM_ACTIVE_OFFERS_PROPORTION:
        statsd.incr(_METRIC_PRIORITIZE_KEEP_PROPORTION)
        return settings.KEEP_PROPORTION_PRIORITY

    return _CLEAR_CLIENT_PRIORITY


async def clear_and_prioritize_waiting_offers() -> None:
    """ Очищаем таблицу заданий и клиентов и проставляем приоритеты заданиям """

    await gen.multi([
        delete_waiting_clients_with_count_off_limit(),
        delete_waiting_offers_for_call_with_count_off_limit()
    ])

    rows = await get_waiting_offer_counts_by_clients()

    clients_count: Dict[str, int] = {row['client_id']: row['waiting_offers_count'] for row in rows}
    clients_priority: Dict[int, List[str]] = defaultdict(list)
    to_clear: List[str] = []
    for client_id in clients_count.keys():
        with new_operation_id():
            priority = await prioritize_client(
                client_id=client_id,
                client_count=clients_count[client_id]
            )
        if priority == _CLEAR_CLIENT_PRIORITY:
            to_clear.append(client_id)
        else:
            clients_priority[priority].append(client_id)

    logger.warning(
        'После приоритизации %d клиентов будут удалены',
        len(to_clear)
    )

    await gen.multi([
        delete_waiting_offers_for_call_by_client_ids(
            client_ids=to_clear
        ),
        delete_waiting_clients_by_client_ids(
            client_ids=to_clear
        )
    ])
    for priority, client_ids in clients_priority.items():
        logger.warning(
            'После приоритизации для %d клиентов будет задан приоритет %d',
            len(client_ids),
            priority
        )

        await set_waiting_offers_priority_by_client_ids(
            client_ids=client_ids,
            priority=priority
        )


async def sync_offers_for_call_with_parsed():
    """ Синхронизировать таблицу заданий offers_for_call и parsed_offers """

    last_sync_date = await get_last_sync_date()
    while parsed_offers := await set_synced_and_fetch_parsed_offers_chunk(last_sync_date=last_sync_date):
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

                client_id = str(uuid.uuid4())
                client = Client(
                    client_id=client_id,
                    avito_user_id=parsed_offer.source_user_id,
                    client_name=client_contact,
                    client_phones=client_phones if client_phones else [],
                    status=ClientStatus.waiting
                )
                await save_client(
                    client=client
                )

            offer_id = str(uuid.uuid4())
            now = datetime.now(tz=pytz.utc)
            offer = Offer(
                id=offer_id,
                parsed_id=parsed_offer.id,
                client_id=client.client_id,
                status=client.status,
                created_at=now,
                synced_at=parsed_offer.timestamp
            )

            await save_offer_for_call(offer=offer)

    await clear_and_prioritize_waiting_offers()
