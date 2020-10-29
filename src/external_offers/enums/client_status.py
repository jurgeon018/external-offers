from dataclasses import dataclass

from cian_enum import StrEnum


@dataclass
class ClientStatus(StrEnum):
    active = 'active'
    """Активный клиент"""
    declined = 'declined'
    """Получен отказ от клиента"""
