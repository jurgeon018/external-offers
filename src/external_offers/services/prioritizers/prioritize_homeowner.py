import logging
from typing import List

from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException
from simple_settings import settings

from external_offers.entities import HomeownerClientChooseMainProfileResult
from external_offers.entities.clients import Client
from external_offers.helpers.phonenumber import transform_phone_number_to_canonical_format
from external_offers.repositories.postgresql import set_cian_user_id_by_client_id
from external_offers.repositories.users import v2_get_users_by_phone
from external_offers.repositories.users.entities import UserModelV2, V2GetUsersByPhone


logger = logging.getLogger(__name__)

_CLEAR_CLIENT_PRIORITY = -1

_METRIC_PRIORITIZE_FAILED = 'prioritize_client.failed'
_METRIC_PRIORITIZE_NO_LK = 'prioritize_client.no_lk'
_METRIC_PRIORITIZE_NO_ACTIVE = 'prioritize_client.no_active'
_METRIC_PRIORITIZE_KEEP_PROPORTION = 'prioritize_client.keep_proportion'


def choose_main_homeowner_client_profile(user_profiles: List[UserModelV2]) -> HomeownerClientChooseMainProfileResult:
    """ Ищем активный профиль собственника. Ставим метки заблокированных пользователей """
    has_bad_account = False
    chosen_profile = None

    for profile in user_profiles:
        if profile.state.is_blocked:
            has_bad_account = True
            break

        if (
            profile.state.is_active
            and not profile.is_agent
        ):
            chosen_profile = profile

    return HomeownerClientChooseMainProfileResult(
        has_bad_account=has_bad_account,
        chosen_profile=chosen_profile
    )


async def prioritize_homeowner_client(
    *,
    client: Client,
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
                return settings.NO_LK_HOMEOWNER_PRIORITY

            # Выбираем основной активный профиль собственника,
            # если нашли заблокированные аккаунты - убираем из очереди
            result = choose_main_homeowner_client_profile(response.users)

            if result.has_bad_account:
                return _CLEAR_CLIENT_PRIORITY

            if not result.chosen_profile:
                return settings.NO_LK_HOMEOWNER_PRIORITY

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
            return settings.FAILED_PRIORITY
    return settings.ACTIVE_LK_HOMEOWNER_PRIOTIY