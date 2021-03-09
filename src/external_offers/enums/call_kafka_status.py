from cian_enum import StrEnum


class CallStatus(StrEnum):
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
    accepted = 'accepted'
    """Согласие"""
    phone_changed = 'phone_changed'
    """Изменен номер телефона"""
    main_account_changed = 'main_account_changed'
    """Изменен основной аккаунт для публикации черновика"""
