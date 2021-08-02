from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class AdminError:
    message: str
    """Сообщение ошибки"""
    code: str
    """Код ошибки"""


@dataclass
class AdminResponse:
    success: bool
    """Статус операции"""
    errors: List[AdminError]
    """Список ошибок"""


@dataclass
class AdminUpdateOffersListRequest:
    is_test: bool 
    """Флаг выдачи тестового клиента"""


@dataclass
class AdminDeclineClientRequest:
    client_id: str
    """ID клиента"""


@dataclass
class AdminCallInterruptedClientRequest:
    client_id: str
    """ID клиента"""


@dataclass
class AdminPhoneUnavailableClientRequest:
    client_id: str
    """ID клиента"""


@dataclass
class AdminPromoGivenClientRequest:
    client_id: str
    """ID клиента"""


@dataclass
class AdminDeleteOfferRequest:
    client_id: str
    """ID клиента"""
    offer_id: str
    """ID объявления в админке (!= ID объявления в Циан) """


@dataclass
class AdminAlreadyPublishedOfferRequest:
    client_id: str
    """ID клиента"""
    offer_id: str
    """ID объявления в админке (!= ID объявления в Циан) """


@dataclass
class AdminCallMissedClientRequest:
    client_id: str
    """ID клиента"""


@dataclass
class AdminCallLaterClientRequest:
    client_id: str
    """ID клиента"""
    call_later_datetime: datetime
    """Дата и время следующего звонка"""
