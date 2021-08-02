from dataclasses import dataclass


@dataclass
class UpdateClientCommentRequest:
    client_id: str
    """Идентификатор клиента"""
    comment: str
    """Коментарий к клиенту"""


@dataclass
class UpdateClientCommentResponse:
    success: bool
    """Статус операции"""
    message: str
    """Текст ответа"""
