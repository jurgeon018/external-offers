# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.17.0

"""
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum

from .deal_rent_data import DealRentData
from .object_model import ObjectModel
from .user_data import UserData


class Platform(StrEnum):
    __value_format__ = NoFormat
    web_site = 'webSite'
    android = 'android'
    ios = 'ios'
    upload = 'upload'
    app = 'app'
    qa_autotests = 'qaAutotests'


@dataclass
class PublicationModel:
    """Модель публикации объявления"""

    deal_rent_data: Optional[DealRentData] = None
    """Данные по сделке в аренде, указываемые при публикации объявления"""
    model: Optional[ObjectModel] = None
    """Модель объявления"""
    platform: Optional[Platform] = None
    """Платформа публикации"""
    user_data: Optional[UserData] = None
    """Данные о пользователе, указываемые при публикации объявления"""
    version: Optional[str] = None
    """Версия платформы"""
