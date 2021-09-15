# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.17.0

"""
from dataclasses import dataclass
from datetime import datetime as _datetime
from typing import List, Optional

from cian_enum import NoFormat, StrEnum

from .auction import Auction
from .bargain_terms import BargainTerms
from .building import Building
from .business_shopping_center import BusinessShoppingCenter
from .commercial_specialty import CommercialSpecialty
from .communication import Communication
from .coworking import Coworking
from .cpl_moderation import CplModeration
from .drainage import Drainage
from .electricity import Electricity
from .flags import Flags
from .garage import Garage
from .gas import Gas
from .home_owner import HomeOwner
from .kp import Kp
from .land import Land
from .monthly_income import MonthlyIncome
from .multiposting import Multiposting
from .phone import Phone
from .photo import Photo
from .platform import Platform
from .publish_terms import PublishTerms
from .rent_by_parts import RentByParts
from .swagger_geo import SwaggerGeo
from .video import Video
from .water import Water


class AccessType(StrEnum):
    __value_format__ = NoFormat
    free = 'free'
    """Свободный"""
    pass_system = 'passSystem'
    """Пропускная система"""


class CallTrackingProvider(StrEnum):
    __value_format__ = NoFormat
    beeline = 'beeline'
    mtt = 'MTT'
    mts = 'mts'
    qa = 'qa'


class Category(StrEnum):
    __value_format__ = NoFormat
    bed_rent = 'bedRent'
    """Койко-место"""
    building_rent = 'buildingRent'
    """Здание"""
    building_sale = 'buildingSale'
    """Здание"""
    business_rent = 'businessRent'
    """Готовый бизнес"""
    business_sale = 'businessSale'
    """Готовый бизнес"""
    car_service_rent = 'carServiceRent'
    """Аренда автосервис"""
    car_service_sale = 'carServiceSale'
    """Продажа автосервиса"""
    commercial_land_rent = 'commercialLandRent'
    """Коммерческая земля"""
    commercial_land_sale = 'commercialLandSale'
    """Коммерческая земля"""
    cottage_rent = 'cottageRent'
    """Коттедж"""
    cottage_sale = 'cottageSale'
    """Коттедж"""
    daily_bed_rent = 'dailyBedRent'
    """Посуточная аренда койко-места"""
    daily_flat_rent = 'dailyFlatRent'
    """Посуточная аренда квартиры"""
    daily_house_rent = 'dailyHouseRent'
    """Посуточная аренда дома, дачи, коттеджа"""
    daily_room_rent = 'dailyRoomRent'
    """Посуточная аренда комнаты"""
    domestic_services_rent = 'domesticServicesRent'
    """Аренда помещения под бытовые услуги"""
    domestic_services_sale = 'domesticServicesSale'
    """Продажа помещения под бытовые услуги"""
    flat_rent = 'flatRent'
    """Квартира"""
    flat_sale = 'flatSale'
    """Квартира"""
    flat_share_sale = 'flatShareSale'
    """Доля в квартире"""
    free_appointment_object_rent = 'freeAppointmentObjectRent'
    """Помещение свободного назначения"""
    free_appointment_object_sale = 'freeAppointmentObjectSale'
    """Помещение свободного назначения"""
    garage_rent = 'garageRent'
    """Гараж"""
    garage_sale = 'garageSale'
    """Гараж"""
    house_rent = 'houseRent'
    """Дом/дача"""
    house_sale = 'houseSale'
    """Дом/дача"""
    house_share_rent = 'houseShareRent'
    """Часть дома"""
    house_share_sale = 'houseShareSale'
    """Часть дома"""
    industry_rent = 'industryRent'
    """Производство"""
    industry_sale = 'industrySale'
    """Производство"""
    land_sale = 'landSale'
    """Участок"""
    new_building_flat_sale = 'newBuildingFlatSale'
    """Квартира в новостройке"""
    office_rent = 'officeRent'
    """Офис"""
    office_sale = 'officeSale'
    """Офис"""
    public_catering_rent = 'publicCateringRent'
    """Аренда общепита"""
    public_catering_sale = 'publicCateringSale'
    """Продажа общепита"""
    room_rent = 'roomRent'
    """Комната"""
    room_sale = 'roomSale'
    """Комната"""
    shopping_area_rent = 'shoppingAreaRent'
    """Торговая площадь"""
    shopping_area_sale = 'shoppingAreaSale'
    """Торговая площадь"""
    townhouse_rent = 'townhouseRent'
    """Таунхаус"""
    townhouse_sale = 'townhouseSale'
    """Таунхаус"""
    warehouse_rent = 'warehouseRent'
    """Склад"""
    warehouse_sale = 'warehouseSale'
    """Склад"""


class ConditionRatingType(StrEnum):
    __value_format__ = NoFormat
    excellent = 'excellent'
    """Отличное"""
    good = 'good'
    """Хорошее"""
    satisfactory = 'satisfactory'
    """Удовлетворительное"""


class ConditionType(StrEnum):
    __value_format__ = NoFormat
    cosmetic_repairs_required = 'cosmeticRepairsRequired'
    """Требуется косметический ремонт"""
    design = 'design'
    """Дизайнерский ремонт"""
    finishing = 'finishing'
    """Под чистовую отделку"""
    major_repairs_required = 'majorRepairsRequired'
    """Требуется капитальный ремонт"""
    office = 'office'
    """Офисная отделка"""
    typical = 'typical'
    """Типовой ремонт"""


class CoworkingOfferType(StrEnum):
    __value_format__ = NoFormat
    office = 'office'
    """Офис"""
    fixed_workplace = 'fixedWorkplace'
    """Закрепленное рабочее место"""
    flexible_workplace = 'flexibleWorkplace'
    """Незакрепленное рабочее место"""
    conference_hall = 'conferenceHall'
    """Конференц-зал"""
    meeting_room = 'meetingRoom'
    """Переговорная комната"""


class Decoration(StrEnum):
    __value_format__ = NoFormat
    fine = 'fine'
    """Чистовая"""
    rough = 'rough'
    """Черновая"""
    without = 'without'
    """Без отделки"""


class DrainageType(StrEnum):
    __value_format__ = NoFormat
    central = 'central'
    """Центральная"""
    septic_tank = 'septicTank'
    """Септик"""
    storm = 'storm'
    """Ливневая"""
    treatment_facilities = 'treatmentFacilities'
    """Очистные сооружения"""


class DrivewayType(StrEnum):
    __value_format__ = NoFormat
    no = 'no'
    """Нет"""
    asphalt = 'asphalt'
    """Асфальтированная дорога"""
    ground = 'ground'
    """Грунтовая дорога"""


class ElectricityType(StrEnum):
    __value_format__ = NoFormat
    border = 'border'
    """По границе участка"""
    main = 'main'
    """Магистральное"""
    transformer_vault = 'transformerVault'
    """Трансформаторная будка"""


class EstateType(StrEnum):
    __value_format__ = NoFormat
    owned = 'owned'
    """В собственности"""
    rent = 'rent'
    """В аренде"""


class FlatType(StrEnum):
    __value_format__ = NoFormat
    open_plan = 'openPlan'
    """Свободная планировка"""
    rooms = 'rooms'
    """Комнаты"""
    studio = 'studio'
    """Студия"""


class FloorMaterialType(StrEnum):
    __value_format__ = NoFormat
    polymeric = 'polymeric'
    """Полимерный"""
    concrete = 'concrete'
    """Бетон"""
    linoleum = 'linoleum'
    """Линолеум"""
    asphalt = 'asphalt'
    """Асфальт"""
    tile = 'tile'
    """Плитка"""
    self_leveling = 'selfLeveling'
    """Наливной"""
    reinforced_concrete = 'reinforcedConcrete'
    """Железобетон"""
    wood = 'wood'
    """Деревянный"""
    laminate = 'laminate'
    """Ламинат"""


class FurniturePresence(StrEnum):
    __value_format__ = NoFormat
    no = 'no'
    """Нет"""
    optional = 'optional'
    """По желанию"""
    yes = 'yes'
    """Есть"""


class GasType(StrEnum):
    __value_format__ = NoFormat
    border = 'border'
    """По границе участка"""
    main = 'main'
    """Магистральное"""


class InputType(StrEnum):
    __value_format__ = NoFormat
    common_from_street = 'commonFromStreet'
    """Общий с улицы"""
    common_from_yard = 'commonFromYard'
    """Общий со двора"""
    separate_from_street = 'separateFromStreet'
    """Отдельный с улицы"""
    separate_from_yard = 'separateFromYard'
    """Отдельный со двора"""


class Layout(StrEnum):
    __value_format__ = NoFormat
    cabinet = 'cabinet'
    """Кабинетная"""
    mixed = 'mixed'
    """Смешанная"""
    open_space = 'openSpace'
    """Открытая"""
    corridorplan = 'corridorplan'
    """Коридорная"""


class PermittedUseType(StrEnum):
    __value_format__ = NoFormat
    agricultural = 'agricultural'
    """Cельскохозяйственное использование"""
    individual_housing_construction = 'individualHousingConstruction'
    """Индивидуальное жилищное строительство (ИЖС)"""
    lowrise_housing = 'lowriseHousing'
    """Малоэтажное жилищное строительство (МЖС)"""
    highrise_buildings = 'highriseBuildings'
    """Высотная застройка"""
    public_use_of_capital_construction = 'publicUseOfCapitalConstruction'
    """Общественное использование объектов капитального строительства"""
    business_management = 'businessManagement'
    """Деловое управление"""
    shopping_centers = 'shoppingCenters'
    """Торговые центры"""
    hotel_amenities = 'hotelAmenities'
    """Гостиничное обслуживание"""
    service_vehicles = 'serviceVehicles'
    """Обслуживание автотранспорта"""
    leisure = 'leisure'
    """Отдых (рекреация)"""
    industry = 'industry'
    """Промышленность"""
    warehouses = 'warehouses'
    """Склады"""
    common_use_area = 'commonUseArea'
    """Общее пользование территории"""


class PlacementType(StrEnum):
    __value_format__ = NoFormat
    shopping_mall = 'shoppingMall'
    """Помещение в торговом комплексе"""
    street_retail = 'streetRetail'
    """Street retail"""


class PropertyType(StrEnum):
    __value_format__ = NoFormat
    building = 'building'
    """здание"""
    free_appointment = 'freeAppointment'
    """помещение свободного назначения"""
    garage = 'garage'
    """гараж"""
    industry = 'industry'
    """производство"""
    land = 'land'
    """земля"""
    office = 'office'
    """офис"""
    shopping_area = 'shoppingArea'
    """торговая площадь"""
    warehouse = 'warehouse'
    """склад"""


class ReadyBusinessType(StrEnum):
    __value_format__ = NoFormat
    rental_business = 'rentalBusiness'
    """Арендный бизнес"""
    other = 'other'
    """Другое"""


class RepairType(StrEnum):
    __value_format__ = NoFormat
    cosmetic = 'cosmetic'
    """Косметический"""
    design = 'design'
    """Дизайнерский"""
    euro = 'euro'
    """Евроремонт"""
    no = 'no'
    """Без ремонта"""


class RoomType(StrEnum):
    __value_format__ = NoFormat
    both = 'both'
    """Оба варианта"""
    combined = 'combined'
    """Совмещенная"""
    separate = 'separate'
    """Изолированная"""


class Source(StrEnum):
    __value_format__ = NoFormat
    website = 'website'
    """Ручная подача"""
    upload = 'upload'
    """Выгрузки"""
    mobile_app = 'mobileApp'
    """Мобильное приложение"""


class Status(StrEnum):
    __value_format__ = NoFormat
    draft = 'Draft'
    """11 - Черновик"""
    published = 'Published'
    """12 - Опубликовано"""
    deactivated = 'Deactivated'
    """14 - Деактивировано (ранее было скрыто Hidden)"""
    refused = 'Refused'
    """15 - Отклонено модератором"""
    deleted = 'Deleted'
    """16 - Удалён"""
    sold = 'Sold'
    """17 - Продано/Сдано"""
    moderate = 'Moderate'
    '18 - Требует модерации\r\nДанный статус исчез - оставим для совместимости'
    removed_by_moderator = 'RemovedByModerator'
    """19 - Удалено модератором"""
    blocked = 'Blocked'
    """20 - объявление снято с публикации по причине применения санкции "приостановки публикации\""""


class WaterType(StrEnum):
    __value_format__ = NoFormat
    central = 'central'
    """Центральное"""
    pumping_station = 'pumpingStation'
    """Водонапорная станция"""
    water_intake_facility = 'waterIntakeFacility'
    """Водозаборный узел"""
    water_tower = 'waterTower'
    """Водонапорная башня"""


class WcLocationType(StrEnum):
    __value_format__ = NoFormat
    indoors = 'indoors'
    """В доме"""
    outdoors = 'outdoors'
    """На улице"""


class WcType(StrEnum):
    __value_format__ = NoFormat
    combined = 'combined'
    """Совмещенный"""
    separate = 'separate'
    """Раздельный"""


class WindowsViewType(StrEnum):
    __value_format__ = NoFormat
    street = 'street'
    """На улицу"""
    yard = 'yard'
    """Во двор"""
    yard_and_street = 'yardAndStreet'
    """На улицу и двор"""


@dataclass
class ObjectModel:
    """Модель объявления."""

    bargain_terms: BargainTerms
    """Условия сделки"""
    category: Category
    """Категория объявления"""
    phones: List[Phone]
    """Телефон"""
    access_type: Optional[AccessType] = None
    """Доступ"""
    additional_phone_lines_allowed: Optional[bool] = None
    """Доп. линии"""
    all_rooms_area: Optional[str] = None
    'Площадь комнат, м².\r\n+ для обозначения смежных комнат, - для раздельных комнат.\r\n            \r\nПоле RoomDefinitions имеет приоритет - если оно задано, поле AllRoomsArea будет переопределено.'
    archived_date: Optional[_datetime] = None
    """Дата переноса объявления в архив."""
    area_parts: Optional[List[RentByParts]] = None
    """Сдача частей в аренду"""
    auction: Optional[Auction] = None
    available_from: Optional[str] = None
    """Дата освобождения"""
    balconies_count: Optional[int] = None
    """Количество балконов"""
    bedrooms_count: Optional[int] = None
    """Количество спален"""
    beds_count: Optional[int] = None
    """Количество спальных мест"""
    building: Optional[Building] = None
    """Информация о здании"""
    business_shopping_center: Optional[BusinessShoppingCenter] = None
    """ТЦ/БЦ, <a href="https://www.cian.ru/cian-api/site/v1/business-shopping-centers-export/to-client-excel/">Скачать список ID</a>"""
    cadastral_number: Optional[str] = None
    """Кадастровый номер"""
    call_tracking_provider: Optional[CallTrackingProvider] = None
    """Тип подключенного calltracking'а"""
    can_parts: Optional[bool] = None
    """Можно частями"""
    children_allowed: Optional[bool] = None
    """Можно с детьми"""
    cian_id: Optional[int] = None
    """ID объявления на ЦИАНе"""
    cian_user_id: Optional[int] = None
    """ID пользователя в ЦИАНе"""
    combined_wcs_count: Optional[int] = None
    """Количество совместных санузлов"""
    communication: Optional[Communication] = None
    """Виды коммуникации с пользователями"""
    condition_rating_type: Optional[ConditionRatingType] = None
    """Состояние"""
    condition_type: Optional[ConditionType] = None
    """Состояние"""
    coworking: Optional[Coworking] = None
    """Коворкинг"""
    coworking_offer_type: Optional[CoworkingOfferType] = None
    """Тип коворкинга"""
    cpl_moderation: Optional[CplModeration] = None
    'Данные для CPL модерации.<br />\r\nЗаполняются данными дольщика из ДДУ<br />\r\nДля физ. лица необходимо указать ФИО, для юр. лица ИНН.<br />\r\nПоля являются обязательными в следующих регионах: Москва, Московская область, Санкт-Петербург, Ленинградская область.'
    creation_date: Optional[_datetime] = None
    """Дата создания объявления"""
    decoration: Optional[Decoration] = None
    """Отделка"""
    description: Optional[str] = None
    """Текст объявления"""
    drainage: Optional[Drainage] = None
    """Канализация"""
    drainage_capacity: Optional[int] = None
    """Объем, м³/сутки"""
    drainage_type: Optional[DrainageType] = None
    """Тип канализации"""
    driveway_type: Optional[DrivewayType] = None
    """Подъездные пути"""
    edit_date: Optional[_datetime] = None
    """Дата редактирования объявления."""
    electricity: Optional[Electricity] = None
    """Электроснабжение"""
    electricity_power: Optional[int] = None
    """Мощность, кВТ"""
    electricity_type: Optional[ElectricityType] = None
    """Тип электроснабжения"""
    emls_id: Optional[str] = None
    """Emls Id объявления"""
    estate_type: Optional[EstateType] = None
    """Недвижимость"""
    feedbox_multi_offer_key: Optional[str] = None
    """Ключ мультиобъявления из Feedbox."""
    flags: Optional[Flags] = None
    """Флаги объявления."""
    flat_type: Optional[FlatType] = None
    """Тип квартиры"""
    floor_from: Optional[int] = None
    """Этаж с"""
    floor_material_type: Optional[FloorMaterialType] = None
    """Материал пола"""
    floor_number: Optional[int] = None
    """Этаж"""
    floor_to: Optional[int] = None
    """Этаж по"""
    furniture_presence: Optional[FurniturePresence] = None
    """Мебель"""
    garage: Optional[Garage] = None
    """Тип гаража"""
    gas: Optional[Gas] = None
    """Газоснабжение"""
    gas_capacity: Optional[int] = None
    """Емкость, м³/час"""
    gas_pressure: Optional[int] = None
    """Давление, Мпа"""
    gas_type: Optional[GasType] = None
    """Тип газоснабжения"""
    geo: Optional[SwaggerGeo] = None
    """Gets or Sets Geo"""
    has_bathhouse: Optional[bool] = None
    """Есть баня"""
    has_bathtub: Optional[bool] = None
    """Есть ванна"""
    has_conditioner: Optional[bool] = None
    """Есть кондиционер"""
    has_dishwasher: Optional[bool] = None
    """Есть посудомоечная машина"""
    has_drainage: Optional[bool] = None
    """Есть канализация"""
    has_electricity: Optional[bool] = None
    """Есть электричество"""
    has_encumbrances: Optional[bool] = None
    """Есть обременение"""
    has_equipment: Optional[bool] = None
    """Есть оборудование"""
    has_extinguishing_system: Optional[bool] = None
    """Есть система пожаротушения"""
    has_fridge: Optional[bool] = None
    """Есть холодильник"""
    has_furniture: Optional[bool] = None
    """Есть мебель в комнатах"""
    has_garage: Optional[bool] = None
    """Есть гараж"""
    has_gas: Optional[bool] = None
    """Есть газ"""
    has_heating: Optional[bool] = None
    """Есть отопление"""
    has_internet: Optional[bool] = None
    """Есть интернет"""
    has_investment_project: Optional[bool] = None
    """Есть инвестпроект"""
    has_kitchen_furniture: Optional[bool] = None
    """Есть мебель на кухне"""
    has_lift: Optional[bool] = None
    """Есть лифт"""
    has_light: Optional[bool] = None
    """Есть свет"""
    has_parking: Optional[bool] = None
    """Есть парковка"""
    has_phone: Optional[bool] = None
    """Есть телефон"""
    has_pool: Optional[bool] = None
    """Есть бассейн"""
    has_ramp: Optional[bool] = None
    """Пандус"""
    has_safe_custody: Optional[bool] = None
    """Ответственное хранение"""
    has_security: Optional[bool] = None
    """Есть охрана"""
    has_shop_windows: Optional[bool] = None
    """Витринные окна"""
    has_shower: Optional[bool] = None
    """Есть душевая кабина"""
    has_transport_services: Optional[bool] = None
    """Транспортные услуги"""
    has_tv: Optional[bool] = None
    """Есть телевизор"""
    has_washer: Optional[bool] = None
    """Есть стиральная машина"""
    has_water: Optional[bool] = None
    """Есть водоснабжение"""
    home_owner: Optional[HomeOwner] = None
    """Информация о собственнике"""
    id: Optional[int] = None
    """ID объявления в Realty"""
    input_type: Optional[InputType] = None
    """Вход"""
    is_apartments: Optional[bool] = None
    """Апартаменты"""
    is_by_commercial_owner: Optional[bool] = None
    """Объявление опубликовано собственником коммерческой"""
    is_by_home_owner: Optional[bool] = None
    """Собственник объявления"""
    is_customs: Optional[bool] = None
    """Таможня"""
    is_enabled_call_tracking: Optional[bool] = None
    """Флаг, показывающий включен ли calltracking"""
    is_in_hidden_base: Optional[bool] = None
    """Размещение в закрытой базе"""
    is_legal_address_provided: Optional[bool] = None
    """Юридический адрес"""
    is_need_hide_exact_address: Optional[bool] = None
    """Если необходимо скрыть точный адрес (адрес в объявлении будет отображаться до улицы)."""
    is_occupied: Optional[bool] = None
    """Помещение занято"""
    is_penthouse: Optional[bool] = None
    """Пентхаус"""
    is_realty_demonstration_enabled: Optional[bool] = None
    """Демонстрация недвижимости доступна"""
    is_rent_by_parts: Optional[bool] = None
    """Сдается ли в аренду частями"""
    is_secret: Optional[bool] = None
    """Объявление в закрытую базу только для специалистов"""
    kitchen_area: Optional[float] = None
    """Площадь кухни, м²"""
    kp: Optional[Kp] = None
    """Коттеджный поселок"""
    land: Optional[Land] = None
    """Информация об участке"""
    layout: Optional[Layout] = None
    """Планировка"""
    layout_photo: Optional[Photo] = None
    ' Планировка.<br />\r\n LayoutPhoto - изображение планировки, если указан isDefault = true, то всегда идет первым. Если указан isDefault = false, фото планировки будет вторым, а первым установится фото со значением isDefault = true тэга Photos. Фото с установленным IsDefault = true всегда перемещается на первое место, а остальные фотографии отображаются в соответствии с порядком, указанным в объявлении. IsDefault = true может быть установлен только для одного Photo или LayoutPhoto.\r\n<a href="https://www.cian.ru/help/quality/qualityrules/">Требования к изображениям.</a>'
    living_area: Optional[float] = None
    """Жилая площадь, м²"""
    loggias_count: Optional[int] = None
    """Количество лоджий"""
    max_area: Optional[float] = None
    """Площадь до"""
    min_area: Optional[float] = None
    """Площадь от"""
    monthly_income: Optional[MonthlyIncome] = None
    """Месячная прибыль"""
    multiposting: Optional[Multiposting] = None
    """Мультипостинг"""
    name: Optional[str] = None
    """Наименование"""
    object_guid: Optional[str] = None
    """Временный ID объявления (GUID)"""
    permitted_use_type: Optional[PermittedUseType] = None
    """Вид разрешённого использования"""
    pets_allowed: Optional[bool] = None
    """Можно с животными"""
    phone_lines_count: Optional[int] = None
    """Кол-во телефонных линий"""
    photos: Optional[List[Photo]] = None
    """Фотографии объекта"""
    placement_type: Optional[PlacementType] = None
    """Тип помещения"""
    platform: Optional[Platform] = None
    """Источник последних изменений"""
    possible_to_change_permitted_use_type: Optional[bool] = None
    """Возможно изменить вид разрешённого использования"""
    project_declaration_url: Optional[str] = None
    """Проектная декларация"""
    property_type: Optional[PropertyType] = None
    """Тип недвижимости"""
    publish_terms: Optional[PublishTerms] = None
    'Условия размещения объявления <br />\r\nСрок размещения платного в аренде жилой - 7 дней, продаже жилой - 30 дней.<br />\r\nСрок размещения платного в аренде коммерческой - 30 дней, продаже коммерческой - 30 дней.<br />\r\nПремиум и Топ размещение - посуточно.<br />\r\nСрок действия Выделенние цветом такой же, как и у размещения на которое вы его добавляете (платное или премиум)'
    published_user_id: Optional[int] = None
    """ID пользователя в Realty от имени которого оно отображается"""
    ready_business_type: Optional[ReadyBusinessType] = None
    """Тип готового бизнеса"""
    rent_by_parts_description: Optional[str] = None
    """Описание сдачи части в аренду"""
    repair_type: Optional[RepairType] = None
    """Тип ремонта"""
    room_area: Optional[float] = None
    """Площадь комнаты (комната, койко-место)"""
    room_type: Optional[RoomType] = None
    """Тип комнаты (комната)"""
    rooms_area: Optional[float] = None
    """Площадь комнат, м²"""
    rooms_count: Optional[int] = None
    """Количество комнат всего"""
    rooms_for_sale_count: Optional[int] = None
    """Количество комнат в продажу/аренду"""
    row_version: Optional[int] = None
    """Версия объявления."""
    separate_wcs_count: Optional[int] = None
    """Количество раздельных санузлов"""
    settlement_name: Optional[str] = None
    """Название коттеджного поселка"""
    share_amount: Optional[str] = None
    """Размер доли в доме"""
    source: Optional[Source] = None
    """Источник объявления"""
    specialty: Optional[CommercialSpecialty] = None
    """Возможное назначение"""
    status: Optional[Status] = None
    """Статус объявления"""
    store_in_hidden_base: Optional[bool] = None
    """Размещение в закрытой базе"""
    tax_number: Optional[int] = None
    """Номер налоговой"""
    title: Optional[str] = None
    """Заголовок объявления. Отображается только для объявлений Премиум и ТОП. Максимальная длина - 33 символа. Минимальная - 8 символов без знаков препинания и пробелов."""
    total_area: Optional[float] = None
    """Общая площадь, м²"""
    user_id: Optional[int] = None
    """ID пользователя в Realty"""
    version: Optional[int] = None
    """Версия модели. Используется для миграции данных."""
    videos: Optional[List[Video]] = None
    """Видео"""
    water: Optional[Water] = None
    """Водоснабжение"""
    water_capacity: Optional[int] = None
    """Объем, м³/сутки"""
    water_pipes_count: Optional[int] = None
    """Количество мокрых точек (водопровод)"""
    water_type: Optional[WaterType] = None
    """Тип водоснабжения"""
    wc_location_type: Optional[WcLocationType] = None
    """Расположение санузла"""
    wc_type: Optional[WcType] = None
    """Тип санузла (комната)"""
    windows_view_type: Optional[WindowsViewType] = None
    """Куда выходят окна"""
    workplace_count: Optional[int] = None
    """Количество рабочих мест"""
