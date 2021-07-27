from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CreateTestClientRequest:
    use_default: bool = True
    """Флаг использования данных дефолтного клиента из настройки"""
    avito_user_id: Optional[str] = None
    """Идентификатор пользователя на Авито"""
    client_phones: Optional[List[str]] = None
    """Телефон клиента"""
    cian_user_id: Optional[str] = None
    """Идентификатор пользователя на Циане"""
    client_name: Optional[str] = None
    """Имя клиента"""
    client_email: Optional[str] = None
    """Почтовый ящик клиента, к которому привязана учетная запись Циана"""
    segment: Optional[str] = None
    """Сегмент пользователя"""
    main_account_chosen: bool = False
    """Флаг выбора главного аккаунта(аккаунт выбранный при первом сохранении черновика)"""


@dataclass
class CreateTestClientResponse:
    success: bool
    message: str
