from dataclasses import dataclass
from typing import Optional

from external_offers.enums.save_offer_status import SaveOfferStatus


@dataclass
class SaveOfferRequest:
    phone_number: str
    """Телефоны"""
    category: str
    """Категория объявления"""
    deal_type: str
    """Тип сделки"""
    offer_type: str
    """Тип недвижимости"""
    realty_type: str
    """Тип жилья"""
    sale_type: str
    """Тип продажи"""
    recovery_password: bool
    """Восстановить ли пароль"""
    address: str
    """Адрес объявления"""
    price: int
    """Цена"""
    total_area: int
    """Общая площадь"""
    floor_number: int
    """Этаж объекта"""
    floors_count: int
    """Общая этажность"""
    rooms_count: Optional[int] = None
    """Количество комнат"""


@dataclass
class SaveOfferResponse:
    status: SaveOfferStatus
    """Статус сохрарнения объявления"""
