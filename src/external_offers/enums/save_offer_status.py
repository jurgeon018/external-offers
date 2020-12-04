from cian_enum import StrEnum


class SaveOfferStatus(StrEnum):
    ok = 'ok'
    """Успешно создан черновик объявления"""
    registration_failed = 'registration_failed'
    """Ошибка при регистрации"""
    geocode_failed = 'geocode_failed'
    """Ошибка при геокодинге"""
    promo_creation_failed = 'promo_creation_failed'
    """Ошибка при создании промокода на публикации"""
    promo_activation_failed = 'promo_activation_failed'
    """Ошибка при применении промокода на публикации"""
    draft_failed = 'draft_failed'
    """Ошибка при создании черновика"""
    already_processing = 'already_processing'
    """Объявление уже в обработке"""
    already_processed = 'already_processed'
    """Объявление уже обработано"""
