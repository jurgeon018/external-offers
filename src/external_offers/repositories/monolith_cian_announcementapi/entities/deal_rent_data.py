# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


class ApplyDealRentSource(StrEnum):
    __value_format__ = NoFormat
    add_form = 'addForm'
    """Форма подачи"""
    after_add_form = 'afterAddForm'
    """После формы подачи"""


class ApplyDealRentVersion(StrEnum):
    __value_format__ = NoFormat
    v1 = 'v1'
    """Сделка V1"""
    v2 = 'v2'
    """Сделка V2"""


@dataclass
class DealRentData:
    """Данные по сделке в аренде, передаваемые при сохранении объявления"""

    apply_deal_rent: Optional[bool] = None
    'Пользователь согласился на подключение услуги "Сделка"\r\nLegacy. Теперь стоит пользоваться applyDealRentVersion'
    apply_deal_rent_source: Optional[ApplyDealRentSource] = None
    """Откуда было произведено согласие на подключение услуги "Сделка\""""
    apply_deal_rent_version: Optional[ApplyDealRentVersion] = None
    """Версия сделки, которую захотел подключить пользователь"""
