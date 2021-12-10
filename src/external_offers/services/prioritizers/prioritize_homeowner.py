import logging
from dataclasses import dataclass
from typing import List, Optional

from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_enum import NoFormat, StrEnum
from cian_http.exceptions import ApiClientException

from external_offers.entities import HomeownerClientChooseMainProfileResult
from external_offers.entities.clients import Client
from external_offers.entities.phones_statuses import AccountPriorities
from external_offers.helpers.phonenumber import transform_phone_number_to_canonical_format
from external_offers.repositories.monolith_cian_profileapi._repo import v1_sanctions_get_sanctions
from external_offers.repositories.monolith_cian_profileapi.entities.v1_sanctions_get_sanctions import (
    V1SanctionsGetSanctions,
)
from external_offers.repositories.postgresql import set_cian_user_id_by_client_id
from external_offers.repositories.users import v2_get_users_by_phone
from external_offers.repositories.users.entities import GetUsersByPhoneResponseV2, UserModelV2, V2GetUsersByPhone
from external_offers.services.prioritizers.build_priority import build_waiting_homeowner_priority


logger = logging.getLogger(__name__)

_CLEAR_CLIENT_PRIORITY = -1

_METRIC_PRIORITIZE_FAILED = 'prioritize_client.failed'
_METRIC_PRIORITIZE_NO_LK = 'prioritize_client.no_lk'


class HomeownerAccountStatus(StrEnum):
    __value_format__ = NoFormat
    clear_client = str(_CLEAR_CLIENT_PRIORITY)
    no_lk_homeowner = 'no_lk_homeowner_priority'
    no_lk_homeowner = 'no_lk_homeowner_priority'
    active_lk_homeowner = 'active_lk_homeowner_priority'


@dataclass
class HomeownerAccontPriority:
    account_status: HomeownerAccountStatus
    new_cian_user_id: Optional[str] = None
    old_cian_user_id: Optional[str] = None


def choose_main_homeowner_client_profile(user_profiles: List[UserModelV2]) -> HomeownerClientChooseMainProfileResult:
    """ Ищем активный профиль собственника. Ставим метки заблокированных пользователей """
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
                or source_user_type.is_n1
                or source_user_type.is_mlsn
                )
        ):
            has_emls_or_subagent = True
            continue

        if (
            profile.state.is_active
            and not profile.is_agent
        ):
            chosen_profile = profile

    return HomeownerClientChooseMainProfileResult(
        has_bad_account=has_bad_account,
        chosen_profile=chosen_profile,
        has_emls_or_subagent=has_emls_or_subagent,
    )


async def find_homeowner_client_account_priority(phone: str) -> HomeownerAccontPriority:

    try:
        response: GetUsersByPhoneResponseV2 = await v2_get_users_by_phone(
            V2GetUsersByPhone(
                phone=phone
            )
        )
        if (
            runtime_settings.CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS
            and response.users
        ):
            # проверяет есть ли по номеру телефона такой аккаунт на циан.
            # если есть - задание пропускается
            # если нет - задание выдается оператору
            return HomeownerAccontPriority(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.clear_client,
            )

        # Приоритет для незарегистрированных собственников
        if not response.users:
            statsd.incr(_METRIC_PRIORITIZE_NO_LK)
            return HomeownerAccontPriority(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.no_lk_homeowner,
            )
        sanctions_response = await v1_sanctions_get_sanctions(
            V1SanctionsGetSanctions(
                user_ids=[user.id for user in response.users],
            )
        )
        if sanctions_response.items:
            return HomeownerAccontPriority(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.clear_client,
            )

        # Выбираем основной активный профиль собственника,
        # если нашли заблокированные аккаунты - убираем из очереди

        result = choose_main_homeowner_client_profile(response.users)

        if result.has_bad_account:
            return HomeownerAccontPriority(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.clear_client,
            )

        if not result.chosen_profile and result.has_emls_or_subagent:
            return HomeownerAccontPriority(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.clear_client,
            )

        if not result.chosen_profile:
            return HomeownerAccontPriority(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.no_lk_homeowner,
            )
        new_cian_user_id = result.chosen_profile.cian_user_id

    except ApiClientException as exc:
        logger.warning(
            'Ошибка при получении идентификатора клиента с номером %s для приоритизации: %s',
            phone,
            exc.message
        )
        statsd.incr(_METRIC_PRIORITIZE_FAILED)
        return HomeownerAccontPriority(
            new_cian_user_id=None,
            account_status=HomeownerAccountStatus.clear_client,
        )

    return HomeownerAccontPriority(
        new_cian_user_id=new_cian_user_id,
        account_status=HomeownerAccountStatus.active_lk_homeowner,
    )


async def prioritize_homeowner_client(
    *,
    client: Client,
    regions: List[int],
    team_settings: dict,
    phones_statuses: dict[str, AccountPriorities],
) -> int:
    old_cian_user_id = client.cian_user_id
    phones = client.client_phones[0]
    phone = transform_phone_number_to_canonical_format(phones)
    if not cian_user_id:

        new_cian_user_id, account_priority = await find_homeowner_client_account_priority(
            phone
        )
    else:
        ...
    if not old_cian_user_id and new_cian_user_id:
        # TODO: понять когда обновлять
        # Обновляем идентификатор клиента
        await set_cian_user_id_by_client_id(
            cian_user_id=new_cian_user_id,
            client_id=client.client_id
        )
    if account_priority == _CLEAR_CLIENT_PRIORITY:
        return account_priority

    return build_waiting_homeowner_priority(
        regions=regions,
        account_priority=account_priority,
        team_settings=team_settings
    )
