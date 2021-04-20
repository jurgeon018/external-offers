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
    '2': 1,
    '4588': 1,
    '1': 2,
    '4593': 2,
    '4612': 3,
    '4557': 4,
    '4603': 5,
    '4599': 6,
    '4623': 7
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

OFFER_TASK_CREATION_FILTER_SUBAGENTS: bool = True
OFFER_TASK_CREATION_FILTER_EMLS: bool = True

SMS_REGISTRATION_TEMPLATE: str = 'Создана учетная запись на ЦИАН. Для входа используйте номер телефона'

PROMOCODE_GROUP_NAME: str = 'packageForAvitoImmigrant_test'
PROMOCODE_POLYGONS: List[int] = [2000]

REGIONS_WITH_PAID_PUBLICATION: List[int] = [1, 2, 4588, 4593]

TEST_OPERATOR_IDS = [58116185]

AVITO_SOURCE_NAME = 'avito'

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

UNDERGROUND_SEARCH_RADIUS = 3000
MAX_GEOCODE_STATIONS = 3

GET_ALL_UNDERGROUNDS_CACHE_TTL = 3600

NEXT_CALL_DAY = 1
NEXT_CALL_HOUR = 10
NEXT_CALL_MINUTES = 0
NEXT_CALL_SECONDS = 0

ITERATE_OVER_LIST_DEFAULT_CHUNK = 100
SET_WAITING_OFFERS_PRIORITY_BY_CLIENT_IDS_CHUNK = 20000

ENABLE_SEND_KAFKA_MESSAGE_FOR_ALREADY_PUBLISHED = False

DEBUG: bool = False
