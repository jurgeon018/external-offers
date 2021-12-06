import re
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from external_offers.enums.external_offer_type import ExternalOfferType
from external_offers.enums.object_model import Category
from external_offers.enums.user_segment import UserSegment
from external_offers.helpers.offer_category import get_types


RE_LAND_AREA = re.compile(r'\d+\.\d+|\d+')
RE_LAND_STATUS_WITH_BRACKETS = re.compile(r'\(\w+\)')
RE_LAND_STATUS_WITHOUT_BRACKETS = re.compile(r'[()]')


@dataclass
class ParsedOfferMessage:
    # https://bitbucket.org/cianmedia/ml-content-copying/src/88105246903268c90e21a31c242160cd9a80b3d9/ml_content_copying/core/runner.py#lines-15:48
    id: str
    """Уникальный ключ"""
    source_object_id: str
    """ID объявления на внешней площадке"""
    source_object_model: dict
    """Данные об объявлении"""
    is_calltracking: Optional[bool]
    """Есть ли коллтрекинг у объявления"""
    timestamp: datetime
    """Дата отправки"""
    source_user_id: Optional[str] = None
    """ID пользователя на внешней площадке"""
    user_segment: Optional[UserSegment] = None
    """Сегмент пользователя"""
    user_subsegment: Optional[str] = None
    """Субсегмент пользователя"""
    source_group_id: Optional[str] = None
    """ID групы обьявлений"""
    is_test: bool = False
    """Флаг тестового обьявления"""
    external_offer_type: Optional[str] = None
    """Тип объявления"""


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
    synced: bool
    """Синхронизировано ли объявление с таблицей заданий"""
    created_at: datetime
    """Дата создания записи в базе"""
    updated_at: datetime
    """Дата обновления записи в базе"""
    source_user_id: Optional[str] = None
    """ID пользователя на внешней площадке"""
    user_segment: Optional[UserSegment] = None
    """Сегмент пользователя"""
    user_subsegment: Optional[str] = None
    """Субсегмент пользователя"""
    source_group_id: Optional[str] = None
    """ID групы обьявлений"""
    is_test: bool = False
    """Флаг тестового обьявления"""
    external_offer_type: Optional[ExternalOfferType] = None
    """Тип объявления"""


@dataclass
class ParsedObjectModel:
    phones: List[str]
    """Телефоны"""
    category: Category
    """Категория объявления"""
    title: str
    """Имя объялвения"""
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
    description: Optional[str] = None
    """Описание объявления"""

    @property
    def is_rent(self) -> bool:
        _, deal_type = get_types(self.category)
        return deal_type.is_rent

    @property
    def is_sale(self) -> bool:
        _, deal_type = get_types(self.category)
        return deal_type.is_sale

    @property
    def is_flat(self) -> bool:
        return self.category in [
            Category.flat_rent,
            Category.flat_sale,
            Category.flat_share_sale,
            Category.daily_flat_rent,
        ]

    @property
    def is_room(self) -> bool:
        return self.category in [
            Category.room_rent,
            Category.room_sale,
            Category.daily_room_rent,
        ]

    @property
    def is_share(self) -> bool:
        return self.category in [
            Category.flat_share_sale
        ]

    @property
    def is_bed(self) -> bool:
        return self.category in [
            Category.bed_rent,
            Category.daily_bed_rent,
        ]

    @property
    def is_allow_rooms(self) -> bool:
        return self.category in [
            Category.flat_rent,
            Category.flat_sale,
            Category.flat_share_sale,
            Category.daily_flat_rent
        ]

    @property
    def is_allow_realty_type(self) -> bool:
        return self.category in [
            Category.flat_rent,
            Category.flat_sale,
            Category.flat_share_sale,
            Category.room_rent,
            Category.room_sale,
            Category.daily_flat_rent,
            Category.daily_room_rent
        ]

    @property
    def is_long_term_rent(self) -> bool:
        return self.category in [
            Category.flat_rent,
            Category.room_rent,
            Category.bed_rent
        ]

    @property
    def is_daily_term_rent(self) -> bool:
        return self.category in [
            Category.daily_bed_rent,
            Category.daily_flat_rent,
            Category.daily_room_rent
        ]

    @property
    def is_suburban_sale(self) -> bool:
        return self.category in [
            Category.cottage_sale,
            Category.house_sale,
            Category.land_sale,
            Category.townhouse_sale
        ]

    @property
    def is_house(self) -> bool:
        return self.category in [
            Category.house_rent,
            Category.house_sale,
            Category.house_share_rent,
            Category.house_share_sale,
        ]

    @property
    def is_cottage(self) -> bool:
        return self.category in [
            Category.cottage_rent,
            Category.cottage_sale,
        ]

    @property
    def is_townhouse(self) -> bool:
        return self.category in [
            Category.townhouse_rent,
            Category.townhouse_sale,
        ]

    @property
    def is_land(self) -> bool:
        return self.category in [
            Category.land_sale,
        ]

    @property
    def land_area(self) -> Optional[float]:
        """
        Получаем площадь участка для загородки (по-другому не получить)
        """
        if self.is_suburban_sale:
            land_area = RE_LAND_AREA.findall(self.title)
            if land_area:
                if self.is_land:
                    return float(land_area[0])
                return float(land_area[1])
        return None

    @property
    def land_status(self) -> Optional[str]:
        """
        Вытаскиеваем регуляркой тип землепользования из тайтла участка
        """
        if self.is_land:
            land_status_list = RE_LAND_STATUS_WITH_BRACKETS.findall(self.title)
            if land_status_list:
                land_status = RE_LAND_STATUS_WITHOUT_BRACKETS.sub('', land_status_list[0])
                return land_status
        return None

    @property
    def land_area_unit(self) -> Optional[str]:
        if self.land_area:
            unit = re.findall(r'сот.|га.', self.title)
            if unit:
                area_unit = 'sotka' if unit[0] == 'сот.' else 'hectare'
                return area_unit
        return None

    # Commercial
    @property
    def is_commercial_type(self) -> bool:
        return self.category in [
            Category.office_sale,
            Category.free_appointment_object_sale,
            Category.shopping_area_sale,
            Category.warehouse_sale,
            Category.industry_sale,
            Category.building_sale,
            Category.business_sale,
            Category.commercial_land_sale,
            Category.office_rent,
            Category.free_appointment_object_rent,
            Category.shopping_area_rent,
            Category.warehouse_rent,
            Category.industry_rent,
            Category.building_rent,
            Category.business_rent,
            Category.commercial_land_rent,
        ]

    @property
    def is_commercial_sale(self) -> bool:
        return self.category in [
            Category.office_sale,
            Category.free_appointment_object_sale,
            Category.shopping_area_sale,
            Category.warehouse_sale,
            Category.industry_sale,
            Category.building_sale,
            Category.business_sale,
            Category.commercial_land_sale,
        ]

    @property
    def is_commercial_rent(self) -> bool:
        return self.category in [
            Category.office_rent,
            Category.free_appointment_object_rent,
            Category.shopping_area_rent,
            Category.warehouse_rent,
            Category.industry_rent,
            Category.building_rent,
            Category.business_rent,
            Category.commercial_land_rent,
        ]

    @property
    def is_office(self) -> bool:
        return self.category in [
            Category.office_rent,
            Category.office_sale,
        ]

    @property
    def is_free_appointment_object(self) -> bool:
        return self.category in [
            Category.free_appointment_object_rent,
            Category.free_appointment_object_sale,
        ]

    @property
    def is_shopping_area(self) -> bool:
        return self.category in [
            Category.shopping_area_rent,
            Category.shopping_area_sale,
        ]

    @property
    def is_warehouse(self) -> bool:
        return self.category in [
            Category.warehouse_rent,
            Category.warehouse_sale,
        ]

    @property
    def is_industry(self) -> bool:
        return self.category in [
            Category.industry_rent,
            Category.industry_sale,
        ]

    @property
    def is_building(self) -> bool:
        return self.category in [
            Category.building_rent,
            Category.building_sale,
        ]

    @property
    def is_business(self) -> bool:
        return self.category in [
            Category.business_rent,
            Category.business_sale,
        ]

    @property
    def is_business_sale(self) -> bool:
        return self.category in [
            Category.business_sale,
        ]

    @property
    def is_commercial_land(self) -> bool:
        return self.category in [
            Category.commercial_land_rent,
            Category.commercial_land_sale,
        ]


@dataclass
class ParsedOfferForCreation:
    id: str
    """Уникальный ключ"""
    contact: str
    """Контактное лицо"""
    timestamp: datetime
    """Дата отправки"""
    created_at: datetime
    """Дата создания"""
    source_user_id: str
    """ID пользователя на внешней площадке"""
    phones: str
    """Номера телефонов в виде JSON списка"""
    user_segment: str
    """Сегмент пользователя"""
    user_subsegment: str
    """Субсегмент пользователя"""
    source_group_id: str
    """ID групы обьявлений"""
    category: str
    """Категория"""
    is_test: bool = False
    """Флаг тестового обьявления"""
    external_offer_type: Optional[ExternalOfferType] = None
    """Тип объявления"""
