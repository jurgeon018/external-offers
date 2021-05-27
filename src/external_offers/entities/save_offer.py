from dataclasses import dataclass
from typing import Optional

from external_offers.enums import SaveOfferCategory, SaveOfferTerm
from external_offers.enums.object_model import DealType, OfferType
from external_offers.enums.save_offer_status import SaveOfferStatus
from external_offers.repositories.monolith_cian_announcementapi.entities.land import Status


@dataclass
class SaveOfferRequest:
    offer_id: str
    """Идентификатор задания"""
    client_id: str
    """Идентификатор клиента"""
    category: SaveOfferCategory
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
    description: str
    """Описание объявления"""
    floor_number: Optional[int] = None
    """Этаж объекта"""
    floors_count: Optional[int] = None
    """Общая этажность"""
    rooms_count: Optional[str] = None
    """Количество комнат"""
    sale_type: Optional[str] = None
    """Тип продажи"""
    realty_type: Optional[str] = None
    """Тип жилья"""
    deposit: Optional[int] = None
    """Залог"""
    prepay_months: Optional[int] = None
    """Предполата за сколько месяцев (до 12)"""
    term_type: Optional[SaveOfferTerm] = None
    """Срок аренды"""
    create_new_account: Optional[bool] = None
    """Создать новый аккаунт"""
    publish_as_homeowner: Optional[bool] = None
    """Опубликовать как собственник"""
    account_for_draft: Optional[int] = None
    """Аккаунт для публикации черновика"""
    land_area: Optional[float] = None
    """Площадь участка для загородки"""
    land_status: Optional[Status] = None
    """Тип землепользования для загородки"""

@dataclass
class SaveOfferResponse:
    status: SaveOfferStatus
    """Статус сохрарнения объявления"""
    message: Optional[str] = ''
    """Информационное сообщение для отображения пользователю"""
