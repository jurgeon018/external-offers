
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


_CLEAR_CLIENT_PRIORITY = -1


class SmbAccountStatus(StrEnum):
    __value_format__ = NoFormat
    no_lk_smb = 'no_lk_smb_priority'
    no_active_smb = 'no_active_smb_priority'
    keep_proportion_smb = 'keep_proportion_smb_priority'
    clear_client = str(_CLEAR_CLIENT_PRIORITY)


@dataclass
class SmbClientAccountPriority:
    """Используется при приоретизации аккаунтов агентов и при записи статусов телефонов в таблицу phones_statuses"""
    account_status: SmbAccountStatus
    """Статус ЛК агента"""
    new_cian_user_id: Optional[str] = None
    """Идентификатор нового агента на циане"""
    old_cian_user_id: Optional[str] = None
    """Идентификатор существующего агента на циане"""


class HomeownerAccountStatus(StrEnum):
    __value_format__ = NoFormat
    no_lk_homeowner = 'no_lk_homeowner_priority'
    active_lk_homeowner = 'active_lk_homeowner_priority'
    clear_client = str(_CLEAR_CLIENT_PRIORITY)


@dataclass
class HomeownerAccountPriority:
    """Используется при приоретизации аккаунтов собственников и при записи статусов телефонов в phones_statuses"""
    account_status: HomeownerAccountStatus
    """Статус ЛК собственника"""
    new_cian_user_id: Optional[str] = None
    """Идентификатор нового собственника на циане"""
    old_cian_user_id: Optional[str] = None
    """Идентификатор существующего собственника на циане"""


@dataclass
class PhoneStatuses:
    """Используется в мапинге при селекте статусов телефонов из phones_statuses"""
    smb_account_status: SmbAccountStatus
    """Статус аккаунта агента"""
    homeowner_account_status: HomeownerAccountStatus
    """Статус аккаунта агента"""
    new_cian_user_id: Optional[int] = None
    """Идентификатор нового пользователя на циане"""
