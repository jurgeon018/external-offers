import logging
from typing import List

from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException

from external_offers.entities import SmbClientChooseMainProfileResult
from external_offers.entities.clients import Client
from external_offers.helpers.phonenumber import transform_phone_number_to_canonical_format
from external_offers.repositories.announcements import v2_get_user_active_announcements_count
from external_offers.repositories.announcements.entities import V2GetUserActiveAnnouncementsCount
from external_offers.repositories.monolith_cian_profileapi._repo import v1_sanctions_get_sanctions
from external_offers.repositories.monolith_cian_profileapi.entities.v1_sanctions_get_sanctions import (
    V1SanctionsGetSanctions,
)
from external_offers.repositories.postgresql import set_cian_user_id_by_client_id
from external_offers.repositories.users import v2_get_users_by_phone
from external_offers.repositories.users.entities import UserModelV2, V2GetUsersByPhone
from external_offers.services.prioritizers.build_priority import build_waiting_smb_priority


logger = logging.getLogger(__name__)

_CLEAR_CLIENT_PRIORITY = -1
_NO_ACTIVE = 0

_METRIC_PRIORITIZE_FAILED = 'prioritize_client.failed'
_METRIC_PRIORITIZE_NO_LK = 'prioritize_client.no_lk'
_METRIC_PRIORITIZE_NO_ACTIVE = 'prioritize_client.no_active'
_METRIC_PRIORITIZE_KEEP_PROPORTION = 'prioritize_client.keep_proportion'


async def choose_main_smb_client_profile(
    user_profiles: List[UserModelV2],
    client_count: int,
    client_id: int,
) -> SmbClientChooseMainProfileResult:
    """Ищем активный профиль smb.Ставим метки заблокированных пользователей,типов источников и активных обьявлений"""
    has_bad_account = False
    has_wrong_user_source_type = False
    chosen_profile = None
    has_bad_offers_proportion = False
    for profile in user_profiles:
        user_source_type = profile.external_user_source_type

        if profile.state.is_blocked:
            has_bad_account = True

        if (
            user_source_type
            and user_source_type.is_sub_agents
        ):
            has_wrong_user_source_type = True
            # не берем клиента в работу если у него есть хоть один субакаунт
            break

        if (
            user_source_type
            and (
                user_source_type.is_emls
                or user_source_type.is_sub_agents
                or user_source_type.is_n1
                or user_source_type.is_mlsn
            )
        ):
            has_wrong_user_source_type = True

        if (
            profile.is_agent
            and profile.state.is_active
        ):
            chosen_profile = profile

        try:
            # Получаем количество активных объявлений для каждого аккаунта пользователя,
            # если хоть в одном не подходит - убираем из очереди.
            active_response = await v2_get_user_active_announcements_count(
                V2GetUserActiveAnnouncementsCount(
                    user_id=profile.cian_user_id
                )
            )
            if (active_response.count / client_count) > runtime_settings.MAXIMUM_ACTIVE_OFFERS_PROPORTION:
                has_bad_offers_proportion = True
                break
        except ApiClientException as exc:
            logger.warning(
                ('Ошибка при получении количества активных объявлений клиента %s'
                    'в аккаунте с cian_user_id %s для приоритизации: %s'),
                client_id,
                profile.cian_user_id,
                exc.message
            )
            has_bad_offers_proportion = True
            break
    return SmbClientChooseMainProfileResult(
        has_bad_account=has_bad_account,
        chosen_profile=chosen_profile,
        has_wrong_user_source_type=has_wrong_user_source_type,
        has_bad_offers_proportion=has_bad_offers_proportion,
    )


async def find_smb_client_account_priority(
    *,
    client: Client,
    client_count: int
) -> int:
    cian_user_id = client.cian_user_id
    if not cian_user_id:
        phone = transform_phone_number_to_canonical_format(client.client_phones[0])

        try:
            response = await v2_get_users_by_phone(
                V2GetUsersByPhone(
                    phone=phone
                )
            )

            # Приоритет для незарегистрированных smb пользователей
            if not response.users:
                statsd.incr(_METRIC_PRIORITIZE_NO_LK)
                return runtime_settings.NO_LK_SMB_PRIORITY

            sanctions_response = await v1_sanctions_get_sanctions(
                V1SanctionsGetSanctions(
                    user_ids=[user.id for user in response.users],
                )
            )
            if sanctions_response.items:
                return _CLEAR_CLIENT_PRIORITY

            # Выбираем основной активный агентский профиль пользователя
            # если нашли заблокированные аккаунты - убираем из очереди
            user_profiles: List[UserModelV2] = response.users
            result = await choose_main_smb_client_profile(
                user_profiles=user_profiles,
                client_count=client_count,
                client_id=client.client_id,
            )
            if result.has_bad_account:
                return _CLEAR_CLIENT_PRIORITY
            if result.has_wrong_user_source_type:
                return _CLEAR_CLIENT_PRIORITY
            if not result.chosen_profile:
                return runtime_settings.NO_LK_SMB_PRIORITY
            if result.has_bad_offers_proportion:
                return _CLEAR_CLIENT_PRIORITY

            cian_user_id = result.chosen_profile.cian_user_id

            # Обновляем идентификатор клиента
            await set_cian_user_id_by_client_id(
                cian_user_id=cian_user_id,
                client_id=client.client_id
                )
        except ApiClientException as exc:
            logger.warning(
                'Ошибка при получении идентификатора клиента %s для приоритизации: %s',
                client.client_id,
                exc.message
            )
            statsd.incr(_METRIC_PRIORITIZE_FAILED)
            return _CLEAR_CLIENT_PRIORITY

    try:
        active_response = await v2_get_user_active_announcements_count(
            V2GetUserActiveAnnouncementsCount(
                user_id=cian_user_id
            )
        )
    except ApiClientException as exc:
        logger.warning(
            'Ошибка при получении количества активных объявлений клиента %s для приоритизации: %s',
            client.client_id,
            exc.message
        )
        statsd.incr(_METRIC_PRIORITIZE_FAILED)
        return _CLEAR_CLIENT_PRIORITY

    # Приоритет по отсутствию активных объявлений на циане
    if active_response.count == _NO_ACTIVE:
        statsd.incr(_METRIC_PRIORITIZE_NO_ACTIVE)
        return runtime_settings.NO_ACTIVE_SMB_PRIORITY

    # Приоритет по доле активных объявлений на циане к спаршенным с других площадок
    if (active_response.count / client_count) <= runtime_settings.MAXIMUM_ACTIVE_OFFERS_PROPORTION:
        statsd.incr(_METRIC_PRIORITIZE_KEEP_PROPORTION)
        return runtime_settings.KEEP_PROPORTION_SMB_PRIORITY

    return _CLEAR_CLIENT_PRIORITY


async def prioritize_smb_client(
    *,
    client: Client,
    client_count: int,
    regions: List[int]
) -> int:
    account_priority = await find_smb_client_account_priority(
        client=client,
        client_count=client_count
    )

    if account_priority == _CLEAR_CLIENT_PRIORITY:
        return account_priority

    return build_waiting_smb_priority(
        regions=regions,
        account_priority=account_priority
    )
