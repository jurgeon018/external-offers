from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateTestClientRequest:
    use_default: bool
    """Флаг использования дефолтных значений при создании тестового клиента"""
    avito_user_id: Optional[str] = None
    """Идентификатор пользователя на Авито"""
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
    client_id: str
    """Идентификатор созданного тестового клиента"""


from external_offers.enums import UserSegment

from dataclasses import dataclass
from typing import Optional



@dataclass
class CreateTestOfferRequest:
    use_default: bool
    """Флаг использования дефолтных значений при создании тестового задания"""
    # clients
    client_id: str
    """ID клиента к которому присвоится задание"""
    # parsed_offers
    parsed_id: Optional[str] = None
    """Уникальный ключ спаршеного обьявления"""
    source_object_id: Optional[str] = None
    """ID объявления на внешней площадке"""
    is_calltracking: Optional[bool] = None
    """Есть ли коллтрекинг у объявления"""
    source_user_id: Optional[str] = None
    """ID пользователя на внешней площадке"""
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
    offer_id: str
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
