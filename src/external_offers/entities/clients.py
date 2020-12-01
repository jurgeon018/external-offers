from dataclasses import dataclass
from typing import List, Optional

from external_offers.enums import ClientStatus


@dataclass
class Client:
    client_id: str
    """Идентификатор клиента"""
    avito_user_id: str
    """Идентификатор пользователя на Авито"""
    client_phones: List[str]
    """Телефон клиента"""
    status: ClientStatus
    """Статус клиента"""
    client_name: Optional[str] = None
    """Имя клиента"""
    cian_user_id: Optional[int] = None
    """Идентификатор пользователя на Циане"""
    client_email: Optional[str] = None
    """Почтовый ящик клиента, к которому привязана учетная запись Циана"""
    operator_user_id: Optional[str] = None
    """Идентификатор оператора, который взял клиента в работу"""
