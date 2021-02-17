from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from external_offers.entities import Offer, ParsedOffer


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
    call_id: str
    """Идентификатор звонка"""
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
    call_id: str
    """Идентификатор звонка"""
    date: datetime
    """Дата события"""
    draft: int
    """Идентификатор созданного черновика"""


@dataclass
class OfferForCallKafkaMessage:
    offer: Offer
    """Стороннее объявления преобразованное в задание (строка в offers_for_call)"""
    operation_id: str
    """Operation id"""
    date: datetime
    """Время отправки"""


@dataclass
class ParsedOfferKafkaMessage:
    offer: ParsedOffer
    """Стороннее объявление (строка в parsed_offers)"""
    operation_id: str
    """Operation id"""
    date: datetime
    """Время отправки"""
