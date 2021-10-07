from dataclasses import dataclass


@dataclass
class UpdateClientAdditionalEmailsRequest:
    client_id: str
    """Идентификатор клиента"""
    additionalEmails: str
    """Причина отказа"""


@dataclass
class UpdateClientAdditionalEmailsResponse:
    success: bool
    """Статус операции"""
    message: str
    """Текст ответа"""
