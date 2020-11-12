# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


class TransportType(StrEnum):
    __value_format__ = NoFormat
    transport = 'transport'
    """На транспорте"""
    walk = 'walk'
    """Пешком"""


@dataclass
class UndergroundInfo:
    cian_id: Optional[int] = None
    """ID линии метро на ЦИАНе"""
    id: Optional[int] = None
    """<a href="http://www.cian.ru/metros-moscow.xml" target="_blank">ID метро в Москве</a> (Int32)<br /><a href="http://www.cian.ru/metros-petersburg.xml" target="_blank">ID метро в Санкт-Петербурге</a> (Int32)<br /><a href="http://www.cian.ru/metros-samara.xml" target="_blank">ID метро в Самаре</a> (Int32)<br /><a href="http://www.cian.ru/metros-nn.xml" target="_blank">ID метро в Нижнем Новгороде</a> (Int32)<br /><a href="http://www.cian.ru/metros-novosibirsk.xml" target="_blank">ID метро в Новосибирске</a> (Int32)<br /><a href="http://www.cian.ru/metros-kazan.xml" target="_blank">ID метро в Казани</a> (Int32)<br /><a href="http://www.cian.ru/metros-ekaterinburg.xml" target="_blank">ID метро в Екатеринбурге</a>"""
    is_default: Optional[bool] = None
    """Признак основной станции метро (если указано несколько)"""
    line_color: Optional[str] = None
    """Цвет линии метро, hex"""
    line_id: Optional[int] = None
    """ID линии метро"""
    name: Optional[str] = None
    """Название"""
    time: Optional[int] = None
    """Время в пути в минутах до метро, мин"""
    transport_type: Optional[TransportType] = None
    """Способ передвижения до метро"""
