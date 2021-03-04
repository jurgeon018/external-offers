from cian_enum import StrEnum


class ReturnClientByPhoneErrorCode(StrEnum):
    failed = 'return_client_failed'
    """Ошибка при возврате клиента в работу"""
    wrong_status = 'wrong_status'
    """Клиент находится в неподходящем для возврата статусе"""
    missing_client = 'missing_client'
    """Клиент не найден"""
