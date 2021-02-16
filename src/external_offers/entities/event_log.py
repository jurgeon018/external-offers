from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from external_offers.enums import ClientStatus, OfferStatus


@dataclass
class EventLogEntry:
    id: str
    """Идентификатор записи в логе"""
    offer_id: str
    """Идентификатор обработанного объявления"""
    operator_user_id: str
    """Идентификатор оператора"""
    status: OfferStatus
    """Статус объявления"""
    created_at: datetime
    """Дата создания объявления"""
    call_id: Optional[str] = None
    """Идентификатор звонка события"""


@dataclass
class EnrichedEventLogEntry:
    id: str
    """Идентификатор записи в логе"""
    offer_id: str
    """Идентификатор обработанного объявления"""
    operator_user_id: str
    """Идентификатор оператора"""
    cian_user_id: Optional[int]
    """Идентификатор пользователя на Циане"""
    avito_user_id: str
    """Идентификатор пользователя на Авито"""
    client_phones: str
    """Идентификатор пользователя на Авито"""
    offer_cian_id: Optional[int]
    """Идентификатор опубликованного объявления на Циане"""
    status: OfferStatus
    """Статус объявления"""
    client_status: ClientStatus
    """Текущий статус клиента"""
    created_at: datetime
    """Дата создания объявления"""
    call_id: Optional[str] = None
    """Идентификатор звонка события"""
