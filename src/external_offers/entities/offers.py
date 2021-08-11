from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from external_offers.enums import OfferStatus
from external_offers.enums.object_model import Category
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import (
    Status as PublicactionStatus,
)


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
    synced_with_kafka: bool = False
    """Было отправлено в кафку в финальном статусе"""
    row_version: int = 0
    """Версия объявления."""
    publication_status: Optional[PublicactionStatus] = None
    """Статус объявления"""


@dataclass
class OfferForPrioritization:
    id: str
    """Идентификатор объявления для публикации"""
    client_id: str
    """Идентификатор клиента"""
    category: Category
    """Категория обьявления"""


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
    publication_status: Optional[OfferStatus] = None
    """Статус объявления"""
