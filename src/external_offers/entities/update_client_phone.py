from dataclasses import dataclass
from typing import List

from external_offers.enums import UpdateClientPhoneErrorCode


@dataclass
class UpdateClientPhoneError:
    message: str
    """Сообщение ошибки"""
    code: UpdateClientPhoneErrorCode
    """Код ошибки"""


@dataclass
class UpdateClientPhoneRequest:
    client_id: str
    """Идентификатор клиента"""
    phone_number: str
    """Телефон"""


@dataclass
class UpdateClientPhoneResponse:
    success: bool
    """Статус операции"""
    errors: List[UpdateClientPhoneError]
    """Список ошибок"""
