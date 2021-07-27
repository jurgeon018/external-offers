from dataclasses import dataclass
from typing import Optional

from external_offers.entities.save_offer import DealType, OfferType, SaveOfferCategory, SaveOfferTerm


@dataclass
class UpdateOfferCategoryResponse:
    success: bool = True
    """Статус операции"""
    message: str = ''
    """Список ошибок"""


@dataclass
class UpdateOfferCategoryRequest:
    offer_id: str
    term_type: Optional[SaveOfferTerm]
    deal_type: DealType
    offer_type: OfferType
    category_type: SaveOfferCategory
