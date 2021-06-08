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
OFFER_TASK_CREATION_CATEGORIES: List[str] = ['flatSale', 'flatRent', 'flatShareSale']
OFFER_TASK_CREATION_REGIONS: List[int] = []
OFFER_TASK_CREATION_MINIMUM_OFFERS: int = 1
OFFER_TASK_CREATION_MAXIMUM_OFFERS: int = 5
MAXIMUM_ACTIVE_OFFERS_PROPORTION: int = 1

ENABLE_CLEAR_OLD_WAITING_OFFERS_FOR_CALL: bool = False
CLEAR_WAITING_OFFERS_FOR_CALL_AGE_IN_DAYS: int = 14

# Настройки приоритетов в очереди
# Приоритет собирается из 4 частей в число равной длины для всех заданий(для сквозной сортировки)

# 1 часть - статус звонка, все новые задания идут с приоритетом 3 в начале, недозвоны - 2, перезвоны - 1
CALL_LATER_PRIORITY: int = 1
CALL_MISSED_PRIORITY: int = 2
WAITING_PRIORITY: int = 3

# 2 часть - регион, основные регионы из ключей настройки ниже ранжируются по значениям, остальные - все вместе
MAIN_REGIONS_PRIORITY: Dict[str, int] = {
    '2':    1,  # Санкт-Петербург
    '4588': 2,  # Ленинградская
    '1':    3,  # Москва
    '4593': 4,  # Московская
    '4603': 5,  # Пермь
    '4897': 7,  # Новосиб
    '4743': 8,  # Екат
    '4914': 9,  # Омск
    '5048': 10,  # Челябинск
    '4827': 11,  # Красноярск
    '4557': 12,  # Архангельск
    '5024': 13,  # Тюмень
    '4596': 14,  # Нижегородская область
    '181462': 15,  # Республика Крым
    '4615': 16,  # Ставропольский край
    '4584': 17,  # Краснодарский край
    '184723': 18,  # Севастополь
    '4606': 19,  # Ростовская область
    '4574': 20,  # Калининградская область
    '4565': 21,  # Волгоградская область
    '4618': 22,  # Республика Татарстан
    '4567': 23,  # Воронежская область
    '4608': 24,  # Самарская область
    '4568': 25,  # Республика Дагестан
    '4605': 26,  # Псковская область
    '4619': 27,  # Тверская область
    '4614': 28,  # Смоленская область
    '4625': 29,  # Ульяновская область
    '4560': 30,  # Республика Башкортостан
    '4621': 31,  # Тульская область
    '4636': 32,  # Ярославская область
    '4576': 33,  # Калужская область
    '4601': 34,  # Орловская область
    '4607': 35,  # Рязанская область
    '4561': 36,  # Белгородская область
    '4609': 37,  # Саратовская область
    '4564': 38,  # Владимирская область
    '4570': 39,  # Ивановская область
    '4594': 40,  # Мурманская область
    '4613': 41,  # Республика Северная Осетия - Алания
    '4597': 42,  # Новгородская область
    '4591': 43,  # Республика Марий Эл
    '4581': 44,  # Кировская область
    '4566': 45,  # Вологодская область
    '4575': 46,  # Республика Калмыкия
    '4589': 47,  # Липецкая область
    '4592': 48,  # Республика Мордовия
    '4631': 49,  # Чеченская Республика
    '4583': 50,  # Костромская область
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
}
# 3 часть - сегмент: собственник или smb
SMB_PRIORITY: int = 1
HOMEOWNER_PRIORITY: int = 2

# 4 часть - статус учетной записи: нет лк на Циан, нет активных объявлений, соблюдена пропорция заданий в админке
# и уже активных объявлений у клиента, для smb дополнительный приоритет - активный лк
NO_LK_SMB_PRIORITY: int = 1
NO_ACTIVE_SMB_PRIORITY: int = 2
KEEP_PROPORTION_SMB_PRIORITY: int = 3
NO_LK_HOMEOWNER_PRIORITY: int = 1
ACTIVE_LK_HOMEOWNER_PRIORITY: int = 2

# 5 часть - тип сделки: продажа, аренда
SALE_PRIORITY: int = 1
RENT_PRIORITY: int = 2

# 6 часть - тип недвижимости: городская, загородная, комерческая
FLAT_PRIORITY: int = 1
SUBURBAN_PRIORITY: int = 2
COMMERCIAL_PRIORITY: int = 3

OFFER_TASK_CREATION_FILTER_SUBAGENTS: bool = True
OFFER_TASK_CREATION_FILTER_EMLS: bool = True

SMS_REGISTRATION_TEMPLATE: str = 'Создана учетная запись на ЦИАН. Для входа используйте номер телефона'

PROMOCODE_GROUP_NAME: str = 'packageForAvitoImmigrant_test'
PROMOCODE_POLYGONS: List[int] = [2000]

REGIONS_WITH_PAID_PUBLICATION: List[int] = [1, 2, 4588, 4593]

TEST_OPERATOR_IDS = [58116185]

AVITO_SOURCE_NAME = 'avito'
YANDEX_SOURCE_NAME = 'yandex'
DOMCLICK_SOURCE_NAME = 'domclick'

DEFAULT_KAFKA_TIMEOUT = 1

SUITABLE_CATEGORIES_FOR_REPORTING = ['flatSale', 'newBuildingFlatSale']

ENABLE_THIRTY_DURATION = True

ENABLE_OUTDATED_OFFERS_CLEARING = True
ENABLE_WAS_UPDATE_CHECK = True
OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS = 1
OFFER_UPDATE_CHECK_WINDOW_IN_HOURS = 24

OFFERS_FOR_CALL_FOR_KAFKA_FETCH_LIMIT = 10000
PARSED_OFFERS_FOR_KAFKA_FETCH_LIMIT = 10000
DEFAULT_PREFETCH = 500
WAITING_OFFERS_FOR_CALL_PREFETCH = 5000

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
SET_WAITING_OFFERS_PRIORITY_BY_OFFER_IDS_CHUNK = 20000

SUITABLE_EXTERNAL_SOURCES_FOR_SAVE = ['1']
SUITABLE_EXTERNAL_SOURCES_FOR_SEND = ['1']

DEBUG: bool = False
