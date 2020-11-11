from dataclasses import dataclass
from typing import Optional

from external_offers.enums.object_model import DealType, OfferType
from external_offers.enums.save_offer_status import SaveOfferStatus
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import Category


@dataclass
class SaveOfferRequest:
    offer_id: str
    """Идентификатор задания"""
    phone_number: str
    """Телефон"""
    category: str
    """Категория объявления"""
    deal_type: DealType
    """Тип сделки"""
    offer_type: OfferType
    """Тип недвижимости"""
    address: str
    """Адрес объявления"""
    price: int
    """Цена"""
    total_area: int
    """Общая площадь"""
    recovery_password: bool
    """Восстановить ли пароль"""
    floor_number: Optional[int] = None
    """Этаж объекта"""
    floors_count: Optional[int] = None
    """Общая этажность"""
    rooms_count: Optional[int] = None
    """Количество комнат"""
    sale_type: Optional[str] = None
    """Тип продажи"""
    realty_type: Optional[str] = None
    """Тип жилья"""


@dataclass
class SaveOfferResponse:
    status: SaveOfferStatus
    """Статус сохрарнения объявления"""
    message: Optional[str] = ''
    """Информационное сообщение для отображения пользователю"""
