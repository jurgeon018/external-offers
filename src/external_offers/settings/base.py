from typing import List

from cian_core.settings.base import *  # pylint: disable=wildcard-import,unused-wildcard-import


APPLICATION_NAME = 'external-offers'
APPLICATION_DESCRIPTION = 'My short description'
APPLICATION_PACKAGE_NAME = 'external_offers'

CHECK_SERVICES: List[str] = []

SAVE_OFFER_MSG: str = (
    'Клиенту будет создан личный кабинет и отправлены данные для регистрации. '
    'Если у клиента уже есть личный кабинет на Циане, но он не помнит пароль, '
    'отметьте галочку ниже, и мы отправим сообщение с инструкцией по восстановлению пароля'
)

OFFER_TASK_CREATION_FETCH_LIMIT: int = 500
OFFER_TASK_CREATION_SEGMENTS: List[str] = ['c']
OFFER_TASK_CREATION_CATEGORIES: List[str] = ['flatSale', 'flatRent', 'flatShareSale']
OFFER_TASK_CREATION_REGIONS: List[int] = []

SMS_REGISTRATION_TEMPLATE = 'Ваш ID на ЦИАН {0}. Пароль {1}'

PROMOCODE_GROUP_NAME = 'packageForAvitoImmigrant_test'
PROMOCODE_POLYGONS = [2000,]

DEBUG: bool = False
