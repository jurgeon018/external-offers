import logging
from typing import List

from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException
from simple_settings import settings

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


def choose_main_smb_client_profile(user_profiles: List[UserModelV2]) -> SmbClientChooseMainProfileResult:
    """ Ищем активный профиль агента. Ставим метки заблокированных пользователей и ЕМЛС или саб. """
    has_bad_account = False
    has_emls_or_subagent = False
    chosen_profile = None

    for profile in user_profiles:
        source_user_type = profile.external_user_source_type

        if profile.state.is_blocked:
            has_bad_account = True
            break

        if (
            source_user_type
            and (
                source_user_type.is_emls
                or source_user_type.is_sub_agents
                )
        ):
            has_emls_or_subagent = True
            continue

        if (
            profile.is_agent
            and profile.state.is_active
        ):
            chosen_profile = profile

    return SmbClientChooseMainProfileResult(
        has_bad_account=has_bad_account,
        chosen_profile=chosen_profile,
        has_emls_or_subagent=has_emls_or_subagent
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
                return settings.NO_LK_SMB_PRIORITY

            sanctions_response = await v1_sanctions_get_sanctions(
                V1SanctionsGetSanctions(
                    user_ids=[user.id for user in response.users],
                )
            )
            if sanctions_response.items:
                return _CLEAR_CLIENT_PRIORITY

            # Выбираем основной активный агентский профиль пользователя
            result = choose_main_smb_client_profile(response.users)
            if result.has_bad_account:
                return _CLEAR_CLIENT_PRIORITY

            if not result.chosen_profile and result.has_emls_or_subagent:
                return _CLEAR_CLIENT_PRIORITY

            if not result.chosen_profile:
                return settings.NO_LK_SMB_PRIORITY

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
            client.client_id,
            exc.message
        )
        statsd.incr(_METRIC_PRIORITIZE_FAILED)
        return _CLEAR_CLIENT_PRIORITY

    # Приоритет по отсутствию активных объявлений на циане
    if active_response.count == _NO_ACTIVE:
        statsd.incr(_METRIC_PRIORITIZE_NO_ACTIVE)
        return settings.NO_ACTIVE_SMB_PRIORITY

    # Приоритет по доле активных объявлений на циане к спаршенным с других площадок
    if (active_response.count / client_count) <= settings.MAXIMUM_ACTIVE_OFFERS_PROPORTION:
        statsd.incr(_METRIC_PRIORITIZE_KEEP_PROPORTION)
        return settings.KEEP_PROPORTION_SMB_PRIORITY

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
