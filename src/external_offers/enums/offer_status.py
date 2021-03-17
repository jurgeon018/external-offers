from cian_enum import StrEnum


class OfferStatus(StrEnum):
    waiting = 'waiting'
    """Объявление в ожидании"""
    in_progress = 'in_progress'
    """Объявление взято в работу"""
    draft = 'draft'
    """Создан черновик"""
    call_missed = 'call_missed'
    """Недозвон по объявлению"""
    call_later = 'call_later'
    """Позвонить позже"""
    cancelled = 'cancelled'
    """Отмена работы по объявлению оператором"""
    already_published = 'alreadyPublished'
    """Объявление уже есть на сайте"""
    promo_given = 'promo_given'
    """Выдан промокод"""
    phone_unavailable = 'phone_unavailable'
    """Телефон недоступен"""
    call_interrupted = 'call_interrupted'
    """Бросили трубку"""
    declined = 'declined'
    """Отказ клиента"""
    done = 'done'
    """Объявление опубликовано"""
