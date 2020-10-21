from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional

from external_offers.enums import OfferStatus


@dataclass
class Offer:
    id: int
    'Идентификатор объявления для публикации'
    parsed_id: int
    'Идентификатор обработанного объявления'
    client_id: int
    'Идентификатор клиента'
    status: OfferStatus
    'Статус объявления'
    created_at: datetime
    'Дата создания объявления'
    object_model: Dict
    'Модель объявления'
    offer_cian_id: Optional[int] = None
    'Идентификатор объявления на Циане'
    started_at: Optional[datetime] = None
    'Дата попадания объявления в работу'
