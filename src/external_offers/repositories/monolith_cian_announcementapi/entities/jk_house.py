# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.17.0

"""
from dataclasses import dataclass
from typing import Optional

from .flat import Flat


@dataclass
class JkHouse:
    flat: Optional[Flat] = None
    """Квартира"""
    id: Optional[int] = None
    'ID<br />\r\nОбязательное поле для объявлений продажи квартир в новостройке для пользователей на тарифе Застройщик.\r\nПолный список идентификаторов можно получить, обратившись к нам через <a href="https://www.cian.ru/contacts/">форму обратной связи</a>.'
    is_hand_over: Optional[bool] = None
    """Корпус сдан"""
    name: Optional[str] = None
    """Название"""
