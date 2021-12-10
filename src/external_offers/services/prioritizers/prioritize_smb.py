import logging
from typing import Optional

from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException

from external_offers.entities import SmbClientChooseMainProfileResult
from external_offers.entities.clients import Client
from external_offers.entities.phones_statuses import (
    PhoneStatuses, SmbAccountStatus,
    SmbClientAccount,
)
from external_offers.services.prioritizers.utils import get_account_priority
from external_offers.helpers.phonenumber import transform_phone_number_to_canonical_format
from external_offers.repositories.announcements import v2_get_user_active_announcements_count
from external_offers.repositories.announcements.entities import V2GetUserActiveAnnouncementsCount
from external_offers.repositories.monolith_cian_announcementapi.entities.phone import Phone
from external_offers.repositories.monolith_cian_profileapi._repo import v1_sanctions_get_sanctions
from external_offers.repositories.monolith_cian_profileapi.entities.v1_sanctions_get_sanctions import (
    V1SanctionsGetSanctions,
)
from external_offers.repositories.postgresql import set_cian_user_id_by_client_id
from external_offers.repositories.users import v2_get_users_by_phone
from external_offers.repositories.users.entities import GetUsersByPhoneResponseV2, UserModelV2, V2GetUsersByPhone
from external_offers.services.prioritizers.build_priority import build_waiting_smb_priority


logger = logging.getLogger(__name__)

_CLEAR_CLIENT_PRIORITY = -1
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


async def find_smb_client_account_status(phone: str) -> SmbClientAccount:
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
            return SmbClientAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.no_lk_smb,
            )
        sanctions_response = await v1_sanctions_get_sanctions(
            V1SanctionsGetSanctions(
                user_ids=[user.id for user in user_profiles],
            )
        )
        if sanctions_response.items:
            return SmbClientAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.clear_client,
            )
        # Выбираем основной активный агентский профиль пользователя
        # если нашли заблокированные аккаунты - убираем из очереди
        result = await choose_main_smb_client_profile(user_profiles)
        if result.has_bad_account:
            return SmbClientAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.clear_client,
            )
        elif result.has_wrong_user_source_type:
            return SmbClientAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.clear_client,
            )
        elif not result.chosen_profile:
            return SmbClientAccount(
                new_cian_user_id=None,
                account_status=SmbAccountStatus.no_lk_smb,
            )
        else:
            return SmbClientAccount(
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
        return SmbClientAccount(
            new_cian_user_id=None,
            account_status=SmbAccountStatus.clear_client,
        )


async def find_smb_client_account_priority(
    *,
    client_count: int,
    client: Client,
    team_settings: dict,
    phones_statuses: dict[str, PhoneStatuses] = None,
) -> int:
    if phones_statuses is None:
        phones_statuses = {}
    cian_user_id = client.cian_user_id
    if not cian_user_id:
        phone = transform_phone_number_to_canonical_format(client.client_phones[0])
        phone_statuses: Optional[PhoneStatuses] = phones_statuses.get(phone)
        if phone_statuses and phone_statuses.smb_account_status:
            # в таблице phones_statuses есть закешированый статус ЛК клиента,
            # и можно не ходить в шарповые ручки, а достать статусы из базы
            # (только если у клиента еще нет cian_user_id)
            account_priority = get_account_priority(
                account_status=phone_statuses.smb_account_status,
                team_settings=team_settings
            )
            new_cian_user_id = phone_statuses.new_cian_user_id
        else:
            # в таблице phones_statuses нет закешированного статуса ЛК клиента,
            # и нужно сходить в шарповые ручки и достать из них статус,
            # (только если у клиента еще нет cian_user_id)
            account = await find_smb_client_account_status(phone=phone)
            account_priority = get_account_priority(
                account_status=account.account_status,
                team_settings=team_settings
            )
            new_cian_user_id = account.new_cian_user_id
        # Обновляем идентификатор клиента
        if new_cian_user_id:
            await set_cian_user_id_by_client_id(
                cian_user_id=new_cian_user_id,
                client_id=client.client_id
            )
    else:
        # если у клиента уже есть cian_user_id, то выдаем ему приоритет активного собственника
        account_priority = get_account_priority(
            account_status=SmbAccountStatus.active_lk_smb.value,
            team_settings=team_settings,
        )
    await find_smb_client_account_priority_by_announcements_count(
        cian_user_id=cian_user_id,
        new_cian_user_id=new_cian_user_id,
        client_count=client_count,
        client_id=client.client_id,
    )
    await get_bad_offer_proportion(
        user_profiles=user_profiles,
        client_count=client_count,
        client_id=client.client_id,        
    )
    return int(account_priority)


async def get_bad_offer_proportion(
    client_count: int,
    client_id: int,
) -> bool:
    # Проверяет что в одном из аккаунтов клиента есть больше активных обьявлений чем позволено
    has_bad_offers_proportion = False
    for profile in user_profiles:
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
    return has_bad_offers_proportion


async def find_smb_client_account_priority_by_announcements_count(
    cian_user_id: int,
    new_cian_user_id: int,
    client_count: int,
    client_id: str,
) -> SmbAccountStatus:
    try:
        active_response = await v2_get_user_active_announcements_count(
            V2GetUserActiveAnnouncementsCount(
                # TODO: понять что передавать
                user_id=cian_user_id or new_cian_user_id
            )
        )
    except ApiClientException as exc:
        logger.warning(
            'Ошибка при получении количества активных объявлений клиента %s для приоритизации: %s',
            client_id,
            exc.message
        )
        statsd.incr(_METRIC_PRIORITIZE_FAILED)
        return SmbAccountStatus.clear_client
    if active_response.count == _NO_ACTIVE:
        # Приоритет по отсутствию активных объявлений на циане
        statsd.incr(_METRIC_PRIORITIZE_NO_ACTIVE)
        return SmbAccountStatus.no_active_smb
    elif (active_response.count / client_count) <= runtime_settings.MAXIMUM_ACTIVE_OFFERS_PROPORTION:
        # Приоритет по доле активных объявлений на циане к спаршенным с других площадок
        statsd.incr(_METRIC_PRIORITIZE_KEEP_PROPORTION)
        return SmbAccountStatus.keep_proportion_smb
    else:
        return SmbAccountStatus.clear_client


async def prioritize_smb_client(
    *,
    client_count: int,
    client: Client,
    regions: list[int],
    team_settings: dict,
    phones_statuses: dict[str, PhoneStatuses] = None,
) -> int:

    account_priority = await find_smb_client_account_priority(
        client_count=client_count,
        client=client,
        team_settings=team_settings,
        phones_statuses=phones_statuses,        
    )

    if account_priority == _CLEAR_CLIENT_PRIORITY:
        return account_priority

    return build_waiting_smb_priority(
        regions=regions,
        account_priority=account_priority,
        team_settings=team_settings,
    )


def get_account_priority(
    account_status: str,
    team_settings: dict,
) -> int:
    if account_status == SmbAccountStatus.clear_client.value:
        account_priority = int(account_status)
    else:
        account_priority = int(team_settings[account_status])
    return account_priority
