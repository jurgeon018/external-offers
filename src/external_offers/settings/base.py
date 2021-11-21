from typing import Dict, List

from cian_core.settings.base import *  # pylint: disable=wildcard-import,unused-wildcard-import


APPLICATION_NAME = 'external-offers'
APPLICATION_DESCRIPTION = 'My short description'
APPLICATION_PACKAGE_NAME = 'external_offers'

CHECK_SERVICES: List[str] = []

SAVE_OFFER_MSG: str = (
    'Для клиента будет создан личный кабинет и отправлены данные для регистрации. '
    'Если у клиента уже есть личный кабинет на Циане, но он не помнит пароль, '
    'он сможет войти в него по номеру телефона'
)

ENABLE_LAST_SYNC_DATE_FETCHING: bool = True
OFFER_TASK_CREATION_OFFER_FETCH_LIMIT: int = 1000
OFFER_TASK_CREATION_SEGMENTS: List[str] = ['c']
OFFER_TASK_CREATION_CATEGORIES: List[str] = [
    'flatSale',
    'flatRent',
    'flatShareSale',
    'officeSale',
    'warehouseSale',
    'shoppingAreaSale',
    'industrySale',
    'buildingSale',
    'freeAppointmentObjectSale',
    'businessSale',
    'commercialLandSale',
    'publicCateringSale',
    'carServiceSale',
    'domesticServicesSale',
    'officeRent',
    'warehouseRent',
    'shoppingAreaRent',
    'industryRent',
    'buildingRent',
    'freeAppointmentObjectRent',
    'businessRent',
    'commercialLandRent',
    'publicCateringRent',
    'carServiceRent',
    'domesticServicesRent'
]
COMMERCIAL_OFFER_TASK_CREATION_CATEGORIES: List[str] = [    # Все коммерческие категории, кроме гаража
    'officeSale',
    'warehouseSale',
    'shoppingAreaSale',
    'industrySale',
    'buildingSale',
    'freeAppointmentObjectSale',
    'businessSale',
    'commercialLandSale',
    'publicCateringSale',
    'carServiceSale',
    'domesticServicesSale',
    'officeRent',
    'warehouseRent',
    'shoppingAreaRent',
    'industryRent',
    'buildingRent',
    'freeAppointmentObjectRent',
    'businessRent',
    'commercialLandRent',
    'publicCateringRent',
    'carServiceRent',
    'domesticServicesRent'
]
OFFER_TASK_CREATION_REGIONS: List[int] = []
OFFER_TASK_CREATION_MINIMUM_OFFERS: int = 1
OFFER_TASK_CREATION_MAXIMUM_OFFERS: int = 5
MAXIMUM_ACTIVE_OFFERS_PROPORTION: int = 1

ENABLE_CLEAR_OLD_WAITING_OFFERS_FOR_CALL: bool = False
CLEAR_WAITING_OFFERS_FOR_CALL_AGE_IN_DAYS: int = 14

# Настройки приоритетов в очереди
# Приоритет собирается из 7 частей в число равной длины для всех заданий(для сквозной сортировки)

# 1-5 - части приоритета для клиента

# 1 часть - тип клиента: добивочный клиент с неактивированым черновиком, новый клиент
UNACTIVATED_CLIENT_PRIORITY: int = 1
NEW_CLIENT_PRIORITY: int = 2

# 2 часть - статус звонка, все новые задания идут с приоритетом 3 в начале, недозвоны - 2, перезвоны - 1
CALL_LATER_PRIORITY: int = 1
CALL_MISSED_PRIORITY: int = 2
WAITING_PRIORITY: int = 3

# 3 часть - регион, основные регионы из ключей настройки ниже ранжируются по значениям, остальные - все вместе
MAIN_REGIONS_PRIORITY: Dict[str, int] = {
    '2':    1,  # Санкт-Петербург
    '4588': 2,  # Ленинградская
    '1':    3,  # Москва
    '4593': 4,  # Московская
    '4612': 5,  # Свердловская область
    '4897': 6,  # Новосиб
    '4827': 7,  # Красноярск
    '4557': 8,  # Архангельск
    '5024': 9,  # Тюмень
    '5048': 10,  # Челябинск
    '4603': 11,  # Пермь
    '4914': 12,  # Омск
    '4584': 13,  # Краснодарский край
    '181462': 14,  # Республика Крым
    '184723': 15,  # Севастополь
    '4606': 16,  # Ростовская область
    '4565': 17,  # Волгоградская область
    '4567': 18,  # Воронежская область
    '4574': 19,  # Калининградская область
    '4580': 20,  # Кемеровская область
    '4597': 21,  # Новгородская область
    '4560': 22,  # Республика Башкортостан
    '4618': 23,  # Республика Татарстан
    '4608': 24,  # Самарская область
    '4615': 25,  # Ставропольский край
    '4743': 26,  # Екат
    '4596': 27,  # Нижегородская область
    '4618': 28,  # Республика Татарстан
    '4568': 29,  # Республика Дагестан
    '4605': 30,  # Псковская область
    '4619': 31,  # Тверская область
    '4614': 32,  # Смоленская область
    '4625': 33,  # Ульяновская область
    '4560': 34,  # Республика Башкортостан
    '4621': 35,  # Тульская область
    '4636': 36,  # Ярославская область
    '4576': 37,  # Калужская область
    '4601': 38,  # Орловская область
    '4607': 39,  # Рязанская область
    '4561': 40,  # Белгородская область
    '4609': 41,  # Саратовская область
    '4564': 42,  # Владимирская область
    '4570': 43,  # Ивановская область
    '4594': 44,  # Мурманская область
    '4613': 45,  # Республика Северная Осетия - Алания
    '4591': 46,  # Республика Марий Эл
    '4581': 47,  # Кировская область
    '4566': 48,  # Вологодская область
    '4575': 49,  # Республика Калмыкия
    '4589': 50,  # Липецкая область
    '4553': 51,  # Республика Адыгея
    '4617': 52,  # Тамбовская область
    '4579': 53,  # Республика Карелия
    '4582': 54,  # Республика Коми
    '4624': 55,  # Удмуртская Республика
    '4586': 56,  # Курганская область
    '4635': 57,  # Ямало-Ненецкий автономный округ
    '4562': 58,  # Брянская область
    '4602': 59,  # Пензенская область
    '4633': 60,  # Чувашская Республика
    '4629': 61,  # Ханты-Мансийский автономный округ
    '4558': 62,  # Астраханская область
    '4571': 63,  # Республика Ингушетия
    '4587': 64,  # Курская область
    '4600': 65,  # Оренбургская область
    '4585': 66,  # Красноярский край
    '4592': 67,  # Республика Мордовия
    '4583': 68,  # Костромская область
    '4631': 69,  # Чеченская Республика
}
# 4 часть - сегмент: собственник или smb
SMB_PRIORITY: int = 1
HOMEOWNER_PRIORITY: int = 2

# 5 часть - статус учетной записи: нет лк на Циан, нет активных объявлений, соблюдена пропорция заданий в админке
# и уже активных объявлений у клиента, для smb дополнительный приоритет - активный лк
NO_LK_SMB_PRIORITY: int = 1
NO_ACTIVE_SMB_PRIORITY: int = 2
KEEP_PROPORTION_SMB_PRIORITY: int = 3
NO_LK_HOMEOWNER_PRIORITY: int = 1
ACTIVE_LK_HOMEOWNER_PRIORITY: int = 2

# 6-7 - части приоритета для обьявления

# 6 часть - тип сделки: продажа, аренда
SALE_PRIORITY: int = 1
RENT_PRIORITY: int = 2

# 7 часть - тип недвижимости: городская, загородная, комерческая
FLAT_PRIORITY: int = 1
SUBURBAN_PRIORITY: int = 2
COMMERCIAL_PRIORITY: int = 3

OFFER_TASK_CREATION_FILTER_SUBAGENTS: bool = True
OFFER_TASK_CREATION_FILTER_EMLS: bool = True

SMS_REGISTRATION_TEMPLATE: str = 'Создана учетная запись на ЦИАН. Для входа используйте номер телефона'
SMB_WELCOME_INSTRUCTION: str = """
Ваше объявление ожидает бесплатной публикации на Циан:\n
1)Зайдите в кабинет my.cian.ru в раздел «Мои объявления.beta», вкладка «Неактивные»\n
2)Отредактируйте объект: проверьте данные, загрузите фото\n
3)Выберите тариф за 0Р\n
4)Сохраните\n
Готово!
"""
HOMEOWNER_WELCOME_INSTRUCTION: str = """
Ваше объявление ожидает бесплатной публикации на Циан:\n
1)Зайдите на my.cian.ru в раздел «Сводка»\n
2)Отредактируйте объявление с отметкой «Черновик»: проверьте данные, загрузите фото\n
3)Выберите тариф за 0Р\n
4)Сохраните\n
Готово!
"""

RECENTLY_REGISTRATION_CHECK_DELAY: int = 120
PROMOCODE_GROUP_NAME: str = 'packageForAvitoImmigrant_test'
PROMOCODE_POLYGONS: List[int] = [2000]

REGIONS_WITH_PAID_PUBLICATION: List[int] = [1, 2, 4588, 4593]

TEST_OPERATOR_IDS = [58116185, 73478905]

AVITO_SOURCE_NAME = 'avito'
YANDEX_SOURCE_NAME = 'yandex'
DOMCLICK_SOURCE_NAME = 'domclick'

DEFAULT_KAFKA_TIMEOUT = 1
OFFERS_FOR_CALL_CHANGE_KAFKA_TIMEOUT = 1

SUITABLE_CATEGORIES_FOR_REPORTING = ['flatSale', 'newBuildingFlatSale']

ENABLE_THIRTY_DURATION = True

ENABLE_OUTDATED_OFFERS_CLEARING = True
ENABLE_WAS_UPDATE_CHECK = True
OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS = 1
OFFER_UPDATE_CHECK_WINDOW_IN_HOURS = 24

OFFERS_FOR_CALL_FOR_KAFKA_FETCH_LIMIT = 10000
PARSED_OFFERS_FOR_KAFKA_FETCH_LIMIT = 10000
DEFAULT_PREFETCH = 500
OFFERS_FOR_PRIORITIZATION_PREFETCH = 5000

UNDERGROUND_SEARCH_RADIUS = 3000
MAX_GEOCODE_STATIONS = 3

GET_ALL_UNDERGROUNDS_CACHE_TTL = 3600
GET_DISTRICTS_BY_HOUSE_CACHE_TTL = 3600
GET_DISTRICTS_BY_IDS_CACHE_TTL = 3600

NEXT_CALL_DAY = 1
NEXT_CALL_HOUR = 10
NEXT_CALL_MINUTES = 0
NEXT_CALL_SECONDS = 0

ITERATE_OVER_LIST_DEFAULT_CHUNK = 100
ITERATE_OVER_OFFERS_FOR_PRIORITIZATION_BY_CLIENT_IDS_CHUNK = 20000
SET_WAITING_OFFERS_PRIORITY_BY_OFFER_IDS_CHUNK = 20000
DELETE_OLD_OFFERS_CHUNK = 20000
SYNC_OFFERS_FOR_CALL_WITH_KAFKA_BY_IDS_CHUNK = 1000

SUITABLE_EXTERNAL_SOURCES_FOR_SAVE = ['1']
SUITABLE_EXTERNAL_SOURCES_FOR_SEND = ['1']

EXTERNAL_OFFERS_GET_USER_ROLES_TRIES_COUNT = 3
CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS: bool = False

DEBUG: bool = False
ENABLE_TEAM_PRIORITIES: bool = False

# Дефолтные обьекты для тестирования
DEFAULT_TEST_OFFER = """{
    "offer_cian_id": null,
    "offer_priority": 1,
    "parsed_id": "ad49365b-caa3-4d8a-be58-02360ad338d5",
    "is_calltracking": false,
    "user_segment": "c",
    "lat": 55.799034118652344,
    "lng": 37.782142639160156,
    "url": "https://www.avito.ru/moskva/komnaty/komnata_13_m_v_3-k_35_et._1308836235",
    "town": "moscow",
    "price": 11000,
    "title": "room 13 square meters, 2 floor",
    "phone": "3333333333",
    "region": 1,
    "address": "moscow, gagarina street",
    "contact": "test client",
    "category": "flatRent",
    "is_agency": 1,
    "is_studio": null,
    "price_type": 6,
    "total_area": 13,
    "living_area": null,
    "rooms_count": 4,
    "description": "description",
    "floor_number": 3,
    "floors_count": 6,
    "is_developer": null
}"""
DEFAULT_TEST_CLIENT = """{
    "segment":  "c",
    "client_phone": "3333333333",
    "client_name": "test client",
    "cian_user_id": null,
    "client_email": "111@21.11",
    "main_account_chosen": false
}"""
ADMIN_OPERATOR_ROLE: str = 'Cian.PrepositionAdmin'
# TODO: https://jira.cian.tech/browse/CD-116932
# вставить правильное название роли тимлида админки
ADMIN_TEAMLEAD_ROLE: str = 'Cian.AdminTeamleadRole'
