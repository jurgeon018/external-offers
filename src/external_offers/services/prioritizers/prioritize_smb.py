import logging
from typing import Optional

from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException

from external_offers.entities import SmbClientChooseMainProfileResult
from external_offers.entities.client_account_statuses import (
    ClientAccountStatus,
    HomeownerAccountStatus,
    SmbAccount,
    SmbAccountStatus,
)
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
from external_offers.repositories.users.entities import GetUsersByPhoneResponseV2, UserModelV2, V2GetUsersByPhone
from external_offers.services.prioritizers.build_priority import build_waiting_smb_priority


logger = logging.getLogger(__name__)

_CLEAR_PRIORITY = 999999999999999999
_NO_ACTIVE = 0

_METRIC_PRIORITIZE_FAILED = 'prioritize_client.failed'
_METRIC_PRIORITIZE_NO_LK = 'prioritize_client.no_lk'
_METRIC_PRIORITIZE_NO_ACTIVE = 'prioritize_client.no_active'
_METRIC_PRIORITIZE_KEEP_PROPORTION = 'prioritize_client.keep_proportion'


async def choose_main_smb_client_profile(user_profiles: list[UserModelV2]) -> SmbClientChooseMainProfileResult:
    """Ищем активный профиль smb.Ставим метки заблокированных пользователей,типов источников и активных обьявлений"""
    has_bad_account = False
    has_wrong_user_source_type = False
    chosen_profile = None
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

    return SmbClientChooseMainProfileResult(
        has_bad_account=has_bad_account,
        chosen_profile=chosen_profile,
        has_wrong_user_source_type=has_wrong_user_source_type,
    )


async def find_smb_account(phone: str) -> SmbAccount:
    phone = transform_phone_number_to_canonical_format(phone)
    try:
        response: GetUsersByPhoneResponseV2 = await v2_get_users_by_phone(
            V2GetUsersByPhone(
                phone=phone
            )
        )
        user_profiles: list[UserModelV2] = response.users
        # Приоритет для незарегистрированных smb пользователей
        if not user_profiles:
            statsd.incr(_METRIC_PRIORITIZE_NO_LK)
            return SmbAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.no_lk_smb,
            )
        sanctions_response = await v1_sanctions_get_sanctions(
            V1SanctionsGetSanctions(
                user_ids=[user.id for user in user_profiles],
            )
        )
        if sanctions_response.items:
            return SmbAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.has_sanctions,
            )
        # Выбираем основной активный агентский профиль пользователя
        # если нашли заблокированные аккаунты - убираем из очереди
        result = await choose_main_smb_client_profile(user_profiles)
        if result.has_bad_account:
            return SmbAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.has_bad_account,
            )
        if result.has_wrong_user_source_type:
            return SmbAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.has_wrong_user_source_type,
            )
        if not result.chosen_profile:
            return SmbAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.no_lk_smb,
            )
        return SmbAccount(
            new_cian_user_id=result.chosen_profile.cian_user_id,
            account_status=None,
        )
    except ApiClientException as exc:
        logger.warning(
            'Ошибка при получении идентификатора клиента с номером %s для приоритизации: %s',
            phone,
            exc.message
        )
        statsd.incr(_METRIC_PRIORITIZE_FAILED)
        return SmbAccount(
            new_cian_user_id=None,
            account_status=SmbAccountStatus.api_client_exception,
        )


async def find_smb_client_account_priority(
    *,
    client_count: int,
    client: Client,
    team_settings: dict,
    client_account_statuses: Optional[dict[str, ClientAccountStatus]] = None,
) -> int:
    phone = client.client_phones[0]
    if client.cian_user_id:
        # если у клиента уже есть cian_user_id, то нужно посчитать активные обьявления
        account_status = await find_smb_client_account_status_by_announcements_count(
            cian_user_id=client.cian_user_id,
            client_count=client_count,
            client_id=client.client_id,
        )
    else:
        if client_account_statuses is None:
            client_account_statuses = {}
        account: Optional[ClientAccountStatus] = client_account_statuses.get(phone)
        if account:
            # в таблице client_account_statuses есть закешированый статус ЛК клиента,
            # и можно не ходить в шарповые ручки, а достать статусы из базы
            account_status: Optional[SmbAccountStatus] = account.smb_account_status
            if account_status is None:
                account_status = account.homeowner_account_status
                logger.warning(
                    'account %s(%s) doesnt have smb_account_status',
                    account,
                    phone,
                )
        else:
            # в таблице client_account_statuses нет закешированного статуса ЛК клиента,
            # и нужно сходить в шарповые ручки и достать из них статус,
            account: SmbAccount = await find_smb_account(phone=phone)
            account_status: Optional[SmbAccountStatus] = account.account_status
        if account_status is None:
            # если статуса ЛК нет, то нужно сохранить новый cian_user_id и посчитать активные обьявления
            # (ответ ручки можно будет потом закешировать)
            account_status = await find_smb_client_account_status_by_announcements_count(
                cian_user_id=client.cian_user_id,
                client_count=client_count,
                client_id=client.client_id,
            )
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


async def prioritize_smb_client(
    *,
    client_count: int,
    client: Client,
    regions: list[int],
    team_settings: dict,
    client_account_statuses: Optional[dict[str, ClientAccountStatus]] = None,
) -> int:

    account_priority: int = await find_smb_client_account_priority(
        client_count=client_count,
        client=client,
        team_settings=team_settings,
        client_account_statuses=client_account_statuses,
    )

    if account_priority == _CLEAR_PRIORITY:
        return account_priority

    return build_waiting_smb_priority(
        regions=regions,
        account_priority=account_priority,
        team_settings=team_settings,
    )


async def find_smb_client_account_status_by_announcements_count(
    cian_user_id: int,
    client_count: int,
    client_id: str,
) -> SmbAccountStatus:
    try:
        active_response = await v2_get_user_active_announcements_count(
            V2GetUserActiveAnnouncementsCount(
                user_id=cian_user_id
            )
        )
        if active_response.count == _NO_ACTIVE:
            # Приоритет по отсутствию активных объявлений на циане
            statsd.incr(_METRIC_PRIORITIZE_NO_ACTIVE)
            return SmbAccountStatus.no_active_smb
        if (active_response.count / client_count) <= runtime_settings.MAXIMUM_ACTIVE_OFFERS_PROPORTION:
            # Приоритет по доле активных объявлений на циане к спаршенным с других площадок
            statsd.incr(_METRIC_PRIORITIZE_KEEP_PROPORTION)
            return SmbAccountStatus.keep_proportion_smb
        return SmbAccountStatus.has_bad_proportion_smb
    except ApiClientException as exc:
        logger.warning(
            'Ошибка при получении количества активных объявлений клиента %s для приоритизации: %s',
            client_id,
            exc.message
        )
        statsd.incr(_METRIC_PRIORITIZE_FAILED)
        return SmbAccountStatus.announcements_api_client_exception
