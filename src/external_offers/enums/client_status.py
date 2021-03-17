from cian_enum import StrEnum


class ClientStatus(StrEnum):
    waiting = 'waiting'
    """В ожидании"""
    declined = 'declined'
    """Получен отказ от клиента"""
    in_progress = 'in_progress'
    """Взят в работу"""
    call_later = 'call_later'
    """Позвонить позже"""
    call_missed = 'call_missed'
    """Недозвон"""
    promo_given = 'promo_given'
    """Выдан промокод"""
    phone_unavailable = 'phone_unavailable'
    """Телефон недоступен"""
    call_interrupted = 'call_interrupted'
    """Бросили трубку"""
    accepted = 'accepted'
    """Согласие"""
