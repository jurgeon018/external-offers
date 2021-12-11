import logging
from typing import Optional

from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException

from external_offers.entities import HomeownerClientChooseMainProfileResult
from external_offers.entities.client_account_statuses import (
    ClientAccountStatus,
    HomeownerAccount,
    HomeownerAccountStatus,
)
from external_offers.entities.clients import Client
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


def choose_main_homeowner_client_profile(user_profiles: list[UserModelV2]) -> HomeownerClientChooseMainProfileResult:
    """ Ищем активный профиль собственника. Ставим метки заблокированных пользователей """
    has_bad_account = False
    has_wrong_user_source_type = False
    chosen_profile = None
    for profile in user_profiles:
        user_source_type = profile.external_user_source_type

        if profile.state.is_blocked:
            has_bad_account = True
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
            continue

        if (
            profile.state.is_active
            and not profile.is_agent
        ):
            chosen_profile = profile

    return HomeownerClientChooseMainProfileResult(
        has_bad_account=has_bad_account,
        chosen_profile=chosen_profile,
        has_wrong_user_source_type=has_wrong_user_source_type,
    )


async def find_homeowner_client_account_status(phone: str) -> HomeownerAccount:
    try:
        response: GetUsersByPhoneResponseV2 = await v2_get_users_by_phone(
            V2GetUsersByPhone(
                phone=phone
            )
        )
        user_profiles: list[UserModelV2] = response.users
        if (
            runtime_settings.CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS
            and user_profiles
        ):
            # проверяет есть ли по номеру телефона такой аккаунт на циан.
            # если есть - задание пропускается
            # если нет - задание выдается оператору
            return HomeownerAccount(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.clear_client,
            )
        # Приоритет для незарегистрированных собственников
        if not user_profiles:
            statsd.incr(_METRIC_PRIORITIZE_NO_LK)
            return HomeownerAccount(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.no_lk_homeowner,
            )
        sanctions_response = await v1_sanctions_get_sanctions(
            V1SanctionsGetSanctions(
                user_ids=[user.id for user in user_profiles],
            )
        )
        if sanctions_response.items:
            return HomeownerAccount(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.clear_client,
            )
        # Выбираем основной активный профиль собственника,
        # если нашли заблокированные аккаунты - убираем из очереди
        result = choose_main_homeowner_client_profile(user_profiles)
        if result.has_bad_account:
            return HomeownerAccount(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.clear_client,
            )
        if not result.chosen_profile and result.has_wrong_user_source_type:
            return HomeownerAccount(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.clear_client,
            )
        if not result.chosen_profile:
            return HomeownerAccount(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.no_lk_homeowner,
            )
        return HomeownerAccount(
            new_cian_user_id=result.chosen_profile.cian_user_id,
            account_status=HomeownerAccountStatus.active_lk_homeowner,
        )
    except ApiClientException as exc:
        logger.warning(
            'Ошибка при получении идентификатора клиента с номером %s для приоритизации: %s',
            phone,
            exc.message
        )
        statsd.incr(_METRIC_PRIORITIZE_FAILED)
        return HomeownerAccount(
            new_cian_user_id=None,
            account_status=HomeownerAccountStatus.clear_client,
        )


async def find_homeowner_client_account_priority(
    *,
    client: Client,
    team_settings: dict,
    client_account_statuses: dict[str, ClientAccountStatus] = None,
) -> int:

    if client.cian_user_id:
        # если у клиента уже есть cian_user_id, то выдаем ему приоритет активного собственника
        return int(team_settings[HomeownerAccountStatus.active_lk_homeowner.value])

    if client_account_statuses is None:
        client_account_statuses = {}

    # если у клиента еще нет cian_user_id
    phone = transform_phone_number_to_canonical_format(client.client_phones[0])
    client_account_status: Optional[ClientAccountStatus] = client_account_statuses.get(phone)

    if client_account_status:
        # в таблице client_account_statuses есть закешированый статус ЛК клиента,
        # и можно не ходить в шарповые ручки, а достать статусы из базы
        account_status = client_account_status.homeowner_account_status
        new_cian_user_id = client_account_status.new_cian_user_id
    else:
        # в таблице client_account_statuses нет закешированного статуса ЛК клиента,
        # и нужно сходить в шарповые ручки и достать из них статус,
        account = await find_homeowner_client_account_status(phone=phone)
        account_status = account.account_status
        new_cian_user_id = account.new_cian_user_id

    if new_cian_user_id:
        # Обновляем идентификатор клиента
        await set_cian_user_id_by_client_id(
            cian_user_id=new_cian_user_id,
            client_id=client.client_id
        )

    if account_status == HomeownerAccountStatus.clear_client:
        return int(account_status.value)
    return int(team_settings[account_status.value])


async def prioritize_homeowner_client(
    *,
    client: Client,
    regions: list[int],
    team_settings: dict,
    client_account_statuses: dict[str, ClientAccountStatus] = None,
) -> int:

    account_priority = await find_homeowner_client_account_priority(
        client=client,
        team_settings=team_settings,
        client_account_statuses=client_account_statuses,
    )

    if account_priority == _CLEAR_CLIENT_PRIORITY:
        return account_priority

    return build_waiting_homeowner_priority(
        regions=regions,
        account_priority=account_priority,
        team_settings=team_settings
    )


def get_account_priority(
    account_status: str,
    team_settings: dict,
) -> int:
    if account_status == HomeownerAccountStatus.clear_client.value:
        account_priority = int(account_status)
    else:
        account_priority = int(team_settings[account_status])
    return account_priority
