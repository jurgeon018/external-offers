from dataclasses import dataclass

from cian_enum import StrEnum


@dataclass
class ClientStatus(StrEnum):
    waiting = 'waiting'
    """В ожидании"""
    declined = 'declined'
    """Получен отказ от клиента"""
    in_progress = 'in_progress'
    """Взят в работу"""
    call_retry = 'call_retry'
    """Позвонить позже"""
    call_missed = 'call_missed'
    """Недозвон"""
    accepted = 'accepted'
    """Согласие"""
