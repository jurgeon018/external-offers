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

OFFER_TASK_CREATION_OFFER_FETCH_LIMIT: int = 1000
OFFER_TASK_CREATION_SEGMENTS: List[str] = ['c']
OFFER_TASK_CREATION_CATEGORIES: List[str] = ['flatSale', 'flatRent', 'flatShareSale']
OFFER_TASK_CREATION_REGIONS: List[int] = []
OFFER_TASK_CREATION_MINIMUM_OFFERS: int = 1
OFFER_TASK_CREATION_MAXIMUM_OFFERS: int = 5

SMS_REGISTRATION_TEMPLATE: str = 'Создана учетная запись на ЦИАН. Для входа используйте номер телефона'

PROMOCODE_GROUP_NAME: str = 'packageForAvitoImmigrant_test'
PROMOCODE_POLYGONS: List[int] = [2000, ]

REGIONS_WITH_PAID_PUBLICATION: List[int] = [1, 2, 4588, 4593]

DEBUG: bool = False
