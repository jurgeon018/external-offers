from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class CallsKafkaMessage:
    manager_id: int
    """Идентификатор оператора"""
    source_user_id: str
    """Идентификатор клиента в админке"""
    user_id: Optional[int]
    """Идентификатор клиента на Циане"""
    phone: str
    """Номер телефона клиента"""
    status: str
    """Статус звонка"""
    date: datetime
    """Дата события"""
    source: str
    """Площадка, с которой объявление"""


@dataclass
class DraftAnnouncementsKafkaMessage:
    manager_id: int
    """Идентификатор оператора"""
    source_user_id: str
    """Идентификатор клиента в админке"""
    user_id: Optional[int]
    """Идентификатор клиента на Циане"""
    phone: str
    """Номер телефона клиента"""
    date: datetime
    """Дата события"""
    draft: int
    """Идентификатор созданного черновика"""