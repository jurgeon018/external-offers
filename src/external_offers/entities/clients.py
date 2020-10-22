from dataclasses import dataclass
from typing import Optional


@dataclass
class Client:
    client_id: int
    """Идентификатор клиента"""
    avito_user_id: int
    """Идентификатор пользователя на Авито"""
    client_name: str
    """Имя клиента"""
    client_phone: str
    """Телефон клиента"""
    realty_user_id: Optional[int] = None
    """Идентификатор пользователя на Циане"""
    client_email: Optional[str] = None
    """Почтовый ящик клиента, к которому привязана учетная запись Циана"""
    operator_user_id: Optional[str] = None
    """Идентификатор оператора, который взял клиента в работу"""
