from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from external_offers.entities import Client, EventLogEntry, Offer, Operator, ParsedOffer, Team
from external_offers.enums import CallStatus


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
    status: CallStatus
    """Статус звонка"""
    call_id: str
    """Идентификатор звонка"""
    date: datetime
    """Дата события"""
    source: str
    """Площадка, с которой объявление"""


@dataclass
class AlreadyPublishedKafkaMessage:
    manager_id: int
    """Идентификатор оператора"""
    source_object_id: str
    """Идентификатор спаршенного объявления"""
    source_user_id: str
    """Идентификатор клиента в админке"""
    phone: str
    """Номер телефона клиента"""
    call_id: str
    """Идентификатор звонка"""
    date: datetime
    """Дата события"""


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


@dataclass
class ClientKafkaMessage:
    client: Client
    """Клиент (строка в clients)"""
    operation_id: str
    """Operation id"""
    date: datetime
    """Время отправки"""


@dataclass
class EventLogKafkaMessage:
    event_log: EventLogEntry
    """Событие перевода по статусам (строка в event_log)"""
    operation_id: str
    """Operation id"""
    date: datetime
    """Время отправки"""


@dataclass
class OperatorKafkaMessage:
    operator: Operator
    """Оператор КЦ (строка в operators)"""
    operation_id: str
    """Operation id"""
    date: datetime
    """Время отправки"""


@dataclass
class TeamKafkaMessage:
    team: Team
    """Команда (строка в teams)"""
    operation_id: str
    """Operation id"""
    date: datetime
    """Время отправки"""
