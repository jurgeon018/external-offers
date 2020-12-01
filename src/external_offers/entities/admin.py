from dataclasses import dataclass
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
class AdminDeclineClientRequest:
    client_id: str
    """ID клиента"""


@dataclass
class AdminDeleteOfferRequest:
    client_id: str
    """ID клиента"""
    offer_id: str
    """ID объявления в админке (!= ID объявления в Циан) """


@dataclass
class AdminCallMissedClientRequest:
    client_id: str
    """ID клиента"""