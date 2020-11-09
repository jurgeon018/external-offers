from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from external_offers.enums import OfferStatus


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
    offer_cian_id: Optional[int] = None
    """Идентификатор объявления на Циане"""
    started_at: Optional[datetime] = None
    """Дата попадания объявления в работу"""
