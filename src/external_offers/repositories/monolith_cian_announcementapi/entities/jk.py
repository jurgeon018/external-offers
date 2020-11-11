# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import Optional

from .developer import Developer
from .jk_house import JkHouse


@dataclass
class Jk:
    """ЖК"""

    developer: Optional[Developer] = None
    """Gets or Sets Developer"""
    house: Optional[JkHouse] = None
    """Корпус"""
    id: Optional[int] = None
    'ID ЖК в базе CIAN<br />\r\nОбязательное поле для объявлений продажи квартир в новостройке.<br />\r\nИдентификатор можно получить из url карточки ЖК:<br /><img src="https://files.cian.ru/files/images/xml_import/doc_jkschema_id.png" width="415px" /><br />\r\nПолный список идентификаторов можно получить, обратившись к нам через <a href="https://www.cian.ru/contacts/">форму обратной связи</a>.'
    name: Optional[str] = None
    """Название ЖК"""
