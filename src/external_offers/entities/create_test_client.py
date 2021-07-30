from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateTestClientRequest:
    use_default: bool
    """Флаг использования дефолтных значений при создании тестового клиента"""
    avito_user_id: Optional[str] = None
    """Идентификатор пользователя на Авито"""
    client_phone: Optional[str] = None
    """Телефон клиента"""
    cian_user_id: Optional[int] = None
    """Идентификатор пользователя на Циане"""
    client_name: Optional[str] = None
    """Имя клиента"""
    client_email: Optional[str] = None
    """Почтовый ящик клиента, к которому привязана учетная запись Циана"""
    segment: Optional[str] = None
    """Сегмент пользователя"""
    main_account_chosen: Optional[bool] = None
    """Флаг выбора главного аккаунта(аккаунт выбранный при первом сохранении черновика)"""


@dataclass
class CreateTestClientResponse:
    success: bool
    """Статус операции"""
    message: str
    """Сообщение"""
    client_id: str
    """Идентификатор созданного тестового клиента"""
