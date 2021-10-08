from dataclasses import dataclass


@dataclass
class UpdateClientAdditionalNumbersRequest:
    client_id: str
    """Идентификатор клиента"""
    additionalNumbers: str
    """Причина отказа"""


@dataclass
class UpdateClientAdditionalNumbersResponse:
    success: bool
    """Статус операции"""
    message: str
    """Текст ответа"""
