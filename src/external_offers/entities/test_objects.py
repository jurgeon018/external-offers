from dataclasses import dataclass
from typing import Optional

from external_offers.enums.user_segment import UserSegment
from external_offers.repositories.monolith_cian_announcementapi.entities.swagger_object_model import (
    Status as PublicationStatus,
)


@dataclass
class CreateTestClientRequest:
    use_default: bool
    """Флаг использования дефолтных значений при создании тестового клиента"""
    source_user_id: str
    """ID пользователя на внешней площадке"""
    client_phone: Optional[str] = None
    """Телефон клиента"""
    cian_user_id: Optional[int] = None
    """Идентификатор пользователя на Циане"""
    client_name: Optional[str] = None
    """Имя клиента"""
    client_email: Optional[str] = None
    """Почтовый ящик клиента, к которому привязана учетная запись Циана"""
    segment: Optional[str] = None
    """Сегмент пользователя"""
    main_account_chosen: Optional[bool] = None
    """Флаг выбора главного аккаунта(аккаунт выбранный при первом сохранении черновика)"""


@dataclass
class CreateTestClientResponse:
    success: bool
    """Статус операции"""
    message: str
    """Сообщение"""
    client_id: Optional[str] = None
    """Идентификатор созданного тестового клиента"""


@dataclass
class CreateTestParsedOfferResponse:
    success: bool
    message: str
    parsed_id: Optional[str] = None


@dataclass
class CreateTestParsedOfferRequest:
    source_object_id: str
    """ID объявления на внешней площадке"""
    is_calltracking: bool
    """Есть ли коллтрекинг у объявления"""
    source_user_id: str
    """ID пользователя на внешней площадке"""
    user_segment: UserSegment
    """Сегмент пользователя"""
    id: Optional[str] = None
    """Уникальный ключ"""
    user_subsegment: Optional[str] = None
    """Субсегмент пользователя"""
    source_group_id: Optional[str] = None
    """ID групы обьявлений"""
    external_offer_type: Optional[str] = None
    """Тип объявления"""

    # source_object_model - Данные об объявлении
    phone: Optional[str] = None
    """Телефон"""
    category: Optional[str] = None
    """Категория объявления"""
    title: Optional[str] = None
    """Имя объялвения"""
    address: Optional[str] = None
    """Адрес объявления"""
    region: Optional[int] = None
    """Регион объявления"""
    price: Optional[int] = None
    """Цена"""
    price_type: Optional[int] = None
    """Справочник "Тип цены"""
    contact: Optional[str] = None
    """Контактное лицо"""
    total_area: Optional[int] = None
    """Общая площадь"""
    floor_number: Optional[int] = None
    """Этаж объекта"""
    floors_count: Optional[int] = None
    """Общая этажность"""
    rooms_count: Optional[int] = None
    """Количество комнат"""
    url: Optional[str] = None
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


@dataclass
class CreateTestOfferRequest:
    use_default: bool
    """Флаг использования дефолтных значений при создании тестового задания"""
    # clients
    source_object_id: str
    """ID объявления на внешней площадке"""
    client_id: Optional[str] = None
    """ID пользователя"""
    source_user_id: Optional[str] = None
    """ID пользователя на внешней площадке"""
    # parsed_offers
    parsed_id: Optional[str] = None
    """Уникальный ключ спаршеного обьявления"""
    is_calltracking: Optional[bool] = None
    """Есть ли коллтрекинг у объявления"""
    user_segment: Optional[str] = None
    """Сегмент пользователя"""
    # offers_for_call
    offer_cian_id: Optional[int] = None
    """Идентификатор объявления на Циане"""
    offer_priority: Optional[int] = None
    """Приоритет задачи"""
    # source_object_model - Данные об объявлении
    phone: Optional[str] = None
    """Телефон"""
    category: Optional[str] = None
    """Категория объявления"""
    title: Optional[str] = None
    """Имя объялвения"""
    address: Optional[str] = None
    """Адрес объявления"""
    region: Optional[int] = None
    """Регион объявления"""
    price: Optional[int] = None
    """Цена"""
    price_type: Optional[int] = None
    """Справочник "Тип цены"""
    contact: Optional[str] = None
    """Контактное лицо"""
    total_area: Optional[int] = None
    """Общая площадь"""
    floor_number: Optional[int] = None
    """Этаж объекта"""
    floors_count: Optional[int] = None
    """Общая этажность"""
    rooms_count: Optional[int] = None
    """Количество комнат"""
    url: Optional[str] = None
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


@dataclass
class CreateTestOfferResponse:
    success: bool
    """Статус операции"""
    message: str
    """Сообщение"""
    offer_id: Optional[str] = None
    """Идентификатор созданного тестового задания"""


@dataclass
class DeleteTestObjectsRequest:
    pass


@dataclass
class DeleteTestObjectsResponse:
    success: bool
    """Статус операции"""
    message: str
    """Сообщение"""


@dataclass
class UpdateTestObjectsPublicationStatusRequest:
    offer_cian_id: int
    """ ID обьявления на циане """
    row_version: int
    """ Версия строки """
    publication_status: Optional[PublicationStatus] = None
    """ Статус публикации """


@dataclass
class UpdateTestObjectsPublicationStatusResponse:
    success: bool
    """ Статус операции """
    message: Optional[str] = None
    """ Текст сообщения """
