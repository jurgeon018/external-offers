from dataclasses import dataclass
from typing import List

from external_offers.enums import ReturnClientByPhoneErrorCode


@dataclass
class ReturnClientByPhoneError:
    message: str
    """Сообщение ошибки"""
    code: ReturnClientByPhoneErrorCode
    """Код ошибки"""


@dataclass
class ReturnClientByPhoneRequest:
    phone_number: str
    """Телефон"""


@dataclass
class ReturnClientByPhoneResponse:
    success: bool
    """Статус операции"""
    errors: List[ReturnClientByPhoneError]
    """Список ошибок"""
