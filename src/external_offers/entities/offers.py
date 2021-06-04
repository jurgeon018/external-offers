from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from click.core import Option

from external_offers.enums import OfferStatus
from external_offers.enums.object_model import Category


@dataclass
class Offer:
    id: str
    """Идентификатор объявления для публикации"""
    parsed_id: str
    """Идентификатор обработанного объявления"""
    client_id: str
    """Идентификатор клиента"""
    status: OfferStatus
    """Статус объявления"""
    created_at: datetime
    """Дата создания объявления"""
    synced_at: datetime
    """Дата последней синхронизации объявления"""
    parsed_created_at: datetime
    """Дата создания спаршенного объявления"""
    priority: Optional[int] = None
    """Приоритет объявления"""
    offer_cian_id: Optional[int] = None
    """Идентификатор объявления на Циане"""
    promocode: Optional[str] = None
    """Промокод для бесплатной публикации"""
    last_call_id: Optional[str] = None
    """Последний идентификатор звонка"""
    started_at: Optional[datetime] = None
    """Дата попадания объявления в работу"""
    category: Optional[str] = None
    """Категория обьявления"""


@dataclass
class OfferForPrioritization:
    id: str
    client_id: str
    category: Category


@dataclass
class EnrichedOffer:
    id: str
    """Идентификатор объявления для публикации"""
    parsed_id: str
    """Идентификатор обработанного объявления"""
    client_id: str
    """Идентификатор клиента"""
    status: OfferStatus
    """Статус объявления"""
    created_at: datetime
    """Дата создания объявления"""
    synced_at: datetime
    """Дата последней синхронизации объявления"""
    offer_cian_id: Optional[int] = None
    """Идентификатор объявления на Циане"""
    promocode: Optional[str] = None
    """Промокод для бесплатной публикации"""
    started_at: Optional[datetime] = None
    """Дата попадания объявления в работу"""
    address: Optional[str] = None
    """Адрес объявления с Авито"""
    title: Optional[str] = None
    """Название объявления с Авито"""
