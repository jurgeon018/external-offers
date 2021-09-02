from cian_enum import StrEnum


class OfferStatus(StrEnum):
    waiting = 'waiting'
    """Объявление в ожидании"""
    declined = 'declined'
    """Отказ клиента"""
    in_progress = 'in_progress'
    """Объявление взято в работу"""
    call_later = 'call_later'
    """Позвонить позже"""
    call_missed = 'call_missed'
    """Недозвон по объявлению"""
    promo_given = 'promo_given'
    """Выдан промокод"""
    phone_unavailable = 'phone_unavailable'
    """Телефон недоступен"""
    call_interrupted = 'call_interrupted'
    """Бросили трубку"""
    draft = 'draft'
    """Создан черновик"""
    cancelled = 'cancelled'
    """Отмена работы по объявлению оператором"""
    already_published = 'alreadyPublished'
    """Объявление уже есть на сайте"""
    done = 'done'
    """Объявление опубликовано"""
