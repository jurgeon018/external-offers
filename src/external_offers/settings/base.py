from typing import List

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

ENABLE_LAST_SYNC_DATE_FETCHING = True
OFFER_TASK_CREATION_OFFER_FETCH_LIMIT: int = 1000
OFFER_TASK_CREATION_SEGMENTS: List[str] = ['c']
OFFER_TASK_CREATION_CATEGORIES: List[str] = ['flatSale', 'flatRent', 'flatShareSale']
OFFER_TASK_CREATION_REGIONS: List[int] = []
OFFER_TASK_CREATION_MINIMUM_OFFERS: int = 1
OFFER_TASK_CREATION_MAXIMUM_OFFERS: int = 5
MAXIMUM_ACTIVE_OFFERS_PROPORTION = 1

NO_LK_SMB_PRIORITY = 1
NO_ACTIVE_SMB_PRIORITY = 2
KEEP_PROPORTION_SMB_PRIORITY = 3
NO_LK_HOMEOWNER_PRIORITY = 4
ACTIVE_LK_HOMEOWNER_PRIOTIY = 5
FAILED_PRIORITY = 6

OFFER_TASK_CREATION_FILTER_SUBAGENTS = True
OFFER_TASK_CREATION_FILTER_EMLS = True

SMS_REGISTRATION_TEMPLATE: str = 'Создана учетная запись на ЦИАН. Для входа используйте номер телефона'

PROMOCODE_GROUP_NAME: str = 'packageForAvitoImmigrant_test'
PROMOCODE_POLYGONS: List[int] = [2000]

REGIONS_WITH_PAID_PUBLICATION: List[int] = [1, 2, 4588, 4593]

TEST_OPERATOR_IDS = [58116185]

AVITO_SOURCE_NAME = 'avito'

DEFAULT_KAFKA_TIMEOUT = 1

SUITABLE_CATEGORIES_FOR_REPORTING = ['flatSale']

ENABLE_THIRTY_DURATION = True

ENABLE_OUTDATED_OFFERS_CLEARING = True
ENABLE_WAS_UPDATE_CHECK = True
OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS = 1
OFFER_UPDATE_CHECK_WINDOW_IN_HOURS = 24

DEBUG: bool = False
