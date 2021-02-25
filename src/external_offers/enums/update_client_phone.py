from cian_enum import StrEnum


class UpdateClientPhoneErrorCode(StrEnum):
    failed = 'update_phone_failed'
    """Ошибка при обновлении телефона"""
    missing_client = 'missing_client'
    """Отсутствует клиент из запроса"""
