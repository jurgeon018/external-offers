
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

    @classmethod
    def from_str(cls, value: str):
        return {
            'no_lk_smb_priority': cls.no_lk_smb,
            'no_active_smb_priority': cls.no_active_smb,
            'keep_proportion_smb_priority': cls.keep_proportion_smb,
            'has_sanctions': cls.has_sanctions,
            'has_bad_account': cls.has_bad_account,
            'has_wrong_user_source_type': cls.has_wrong_user_source_type,
            'api_client_exception': cls.api_client_exception,
            'has_bad_proportion_smb': cls.has_bad_proportion_smb,
            'announcements_api_client_exception': cls.announcements_api_client_exception,
        }[value]


@dataclass
class SmbAccount:
    """Используется при приоретизации аккаунтов агентов и при записи статусов в таблицу client_account_statuses"""
    account_status: Optional[SmbAccountStatus] = None
    """Статус ЛК агента"""
    new_cian_user_id: Optional[int] = None
    """Идентификатор нового агента на циане"""
    # has_bad_offer_proportion: bool = False
    # """В одном из аккаунтов клиента есть больше активных обьявлений чем позволено"""


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

    @classmethod
    def from_str(cls, value: str):
        return {
            'no_lk_homeowner_priority': cls.no_lk_homeowner,
            'active_lk_homeowner_priority': cls.active_lk_homeowner,
            'has_existing_accounts': cls.has_existing_accounts,
            'has_sanctions': cls.has_sanctions,
            'has_bad_account': cls.has_bad_account,
            'has_wrong_user_source_type': cls.has_wrong_user_source_type,
            'api_client_exception': cls.api_client_exception,
        }[value]


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
    homeowner_account_status: HomeownerAccountStatus
    """Статус аккаунта агента"""
    smb_account_status: Optional[SmbAccountStatus] = None
    """Статус аккаунта агента"""
    new_cian_user_id: Optional[int] = None
    """Идентификатор нового пользователя на циане"""
