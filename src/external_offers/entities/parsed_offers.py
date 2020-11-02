from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from external_offers.enums.user_segment import UserSegment


@dataclass
class ParsedOffer:
    id: str
    """Уникальный ключ"""
    source_object_id: str
    """ID объявления на внешней площадке"""
    source_object_model: dict
    """Данные об объявлении"""
    is_calltracking: bool
    """Есть ли коллтрекинг у объявления"""
    timestamp: datetime
    """Дата отправки"""
    source_user_id: Optional[str] = None
    """ID пользователя на внешней площадке"""
    user_segment: Optional[UserSegment] = None
    """Сегмент пользователя"""


@dataclass
class ParsedObjectModel:
    phones: List[str]
    """Телефоны"""
    category: str
    """Категория объявления"""
    title: str
    """Имя объялвения"""
    description: str
    """Описание объявления"""
    address: str
    """Адрес объявления"""
    region: int
    """Регион объявления"""
    price: int
    """Цена"""
    pricetype: int
    """Справочник "Тип цены"""
    contact: str
    """Контактное лицо"""
    total_area: int
    """Общая площадь"""
    floor_number: int
    """Этаж объекта"""
    floors_count: int
    """Общая этажность"""
    rooms_count: int
    """Количество комнат"""
    url: str
    """URL объявления"""
    is_agency: Optional[bool] = None
    """Агентство"""
    is_developer: Optional[bool] = None
    """От застройщика"""
    is_studio: Optional[bool] = None
    """Является ли квартира студией"""
    town: Optional[str] = None
    """Город"""
    lat: Optional[float] = None
    """Широта"""
    lng: Optional[float] = None
    """Долгота"""
    living_area: Optional[int] = None
    """Жилая площадь"""
