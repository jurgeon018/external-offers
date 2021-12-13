
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


_CLEAR_CLIENT_PRIORITY = -1


class SmbAccountStatus(StrEnum):
    __value_format__ = NoFormat
    # statuses for prioritization
    no_lk_smb = 'no_lk_smb_priority'
    no_active_smb = 'no_active_smb_priority'
    keep_proportion_smb = 'keep_proportion_smb_priority'
    # statuses for cleaning
    has_sanctions = 'has_sanctions'
    has_bad_account = 'has_bad_account'
    has_wrong_user_source_type = 'has_wrong_user_source_type'
    api_client_exception = 'api_client_exception'
    # statuses for active announcements count cleaning
    has_bad_proportion_smb = 'has_bad_proportion_smb'
    announcements_api_client_exception = 'announcements_api_client_exception'


@dataclass
class SmbAccount:
    """Используется при приоретизации аккаунтов агентов и при записи статусов в таблицу client_account_statuses"""
    account_status: Optional[SmbAccountStatus] = None
    """Статус ЛК агента"""
    new_cian_user_id: Optional[int] = None
    """Идентификатор нового агента на циане"""


class HomeownerAccountStatus(StrEnum):
    __value_format__ = NoFormat
    # statuses for prioritization
    no_lk_homeowner = 'no_lk_homeowner_priority'
    active_lk_homeowner = 'active_lk_homeowner_priority'
    # statuses for cleaning
    has_existing_accounts = 'has_existing_accounts'
    has_sanctions = 'has_sanctions'
    has_bad_account = 'has_bad_account'
    has_wrong_user_source_type = 'has_wrong_user_source_type'
    api_client_exception = 'api_client_exception'


@dataclass
class HomeownerAccount:
    """Используется при приоретизации аккаунтов собственников и при записи статусов в client_account_statuses"""
    account_status: HomeownerAccountStatus
    """Статус ЛК собственника"""
    new_cian_user_id: Optional[int] = None
    """Идентификатор нового собственника на циане"""


@dataclass
class ClientAccountStatus:
    """Используется в мапинге при селекте статусов из client_account_statuses"""
    homeowner_account_status: Optional[HomeownerAccountStatus] = None
    """Статус аккаунта агента"""
    smb_account_status: Optional[SmbAccountStatus] = None
    """Статус аккаунта агента"""
    new_cian_user_id: Optional[int] = None
    """Идентификатор нового пользователя на циане"""
