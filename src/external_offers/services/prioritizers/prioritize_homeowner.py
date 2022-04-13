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
    SmbAccountStatus,
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

_CLEAR_PRIORITY = 999999999999999999

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


async def find_homeowner_account(phone: str) -> HomeownerAccount:
    phone = transform_phone_number_to_canonical_format(phone)
    try:
        response: GetUsersByPhoneResponseV2 = await v2_get_users_by_phone(
            V2GetUsersByPhone(
                phone=phone
            )
        )
        user_profiles: list[UserModelV2] = response.users
        if (
            runtime_settings.get('CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS', False)
            and user_profiles
        ):
            # проверяет есть ли по номеру телефона такой аккаунт на циан.
            # если есть - задание пропускается
            # если нет - задание выдается оператору
            return HomeownerAccount(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.has_existing_accounts,
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
                account_status=HomeownerAccountStatus.has_sanctions,
            )
        # Выбираем основной активный профиль собственника,
        # если нашли заблокированные аккаунты - убираем из очереди
        result = choose_main_homeowner_client_profile(user_profiles)
        if result.has_bad_account:
            return HomeownerAccount(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.has_bad_account,
            )
        if not result.chosen_profile and result.has_wrong_user_source_type:
            return HomeownerAccount(
                new_cian_user_id=None,
                account_status=HomeownerAccountStatus.has_wrong_user_source_type,
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
            account_status=HomeownerAccountStatus.api_client_exception,
        )


async def find_homeowner_client_account_priority(
    *,
    client: Client,
    team_settings: dict,
    client_account_statuses: Optional[dict[str, ClientAccountStatus]] = None,
) -> int:
    phone = client.client_phones[0]
    if client.cian_user_id:
        # если у клиента уже есть cian_user_id, то выдаем ему приоритет активного собственника
        account_status = HomeownerAccountStatus.active_lk_homeowner
    else:
        if client_account_statuses is None:
            client_account_statuses = {}
        account: Optional[ClientAccountStatus] = client_account_statuses.get(phone)
        if account:
            # в таблице client_account_statuses есть закешированый статус ЛК клиента,
            # и можно не ходить в шарповые ручки, а достать статусы из базы
            account_status: Optional[HomeownerAccountStatus] = account.homeowner_account_status
            if account_status is None:
                account_status = account.smb_account_status
                logger.warning(
                    'account %s(%s) doesnt have homeowner_account_status',
                    account,
                    phone,
                )
        else:
            # в таблице client_account_statuses нет закешированного статуса ЛК клиента,
            # и нужно сходить в шарповые ручки и достать из них статус,
            account: HomeownerAccount = await find_homeowner_account(phone=phone)
            account_status: Optional[HomeownerAccountStatus] = account.account_status
        if account.new_cian_user_id:
            await set_cian_user_id_by_client_id(
                cian_user_id=account.new_cian_user_id,
                client_id=client.client_id
            )
    logger.warning(
        'У клиента %s(%s) статус аккаунта %s',
        client.client_id,
        phone,
        account_status
    )
    if account_status in [
        HomeownerAccountStatus.has_existing_accounts,
        HomeownerAccountStatus.has_sanctions,
        HomeownerAccountStatus.has_bad_account,
        HomeownerAccountStatus.has_wrong_user_source_type,
        HomeownerAccountStatus.api_client_exception,
        # 
        SmbAccountStatus.has_sanctions,
        SmbAccountStatus.has_bad_account,
        SmbAccountStatus.has_wrong_user_source_type,
        SmbAccountStatus.api_client_exception,
        SmbAccountStatus.has_bad_proportion_smb,
        SmbAccountStatus.announcements_api_client_exception,        
    ]:
        account_priority = _CLEAR_PRIORITY
    elif account_status in [
        HomeownerAccountStatus.no_lk_homeowner,
        HomeownerAccountStatus.active_lk_homeowner,
        #
        SmbAccountStatus.no_lk_smb,
        SmbAccountStatus.no_active_smb,
        SmbAccountStatus.keep_proportion_smb,
    ]:
        account_priority = int(team_settings[account_status.value])
    else:
        raise Exception(f'Unhandled account status: {account_status}, {type(account_status)}')
    return account_priority


async def prioritize_homeowner_client(
    *,
    client: Client,
    regions: list[int],
    team_settings: dict,
    client_account_statuses: Optional[dict[str, ClientAccountStatus]] = None,
) -> int:

    account_priority = await find_homeowner_client_account_priority(
        client=client,
        team_settings=team_settings,
        client_account_statuses=client_account_statuses,
    )

    if account_priority == _CLEAR_PRIORITY:
        return account_priority

    return build_waiting_homeowner_priority(
        regions=regions,
        account_priority=account_priority,
        team_settings=team_settings
    )
