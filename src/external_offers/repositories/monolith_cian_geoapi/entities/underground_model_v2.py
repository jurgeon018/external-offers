# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-geoapi`

cian-codegen version: 1.9.0

"""
from dataclasses import dataclass
from datetime import datetime as _datetime
from typing import List, Optional

from .line_model import LineModel
from .underground_entrance import UndergroundEntrance


@dataclass
class UndergroundModelV2:
    """Модель метро"""

    cian_id: Optional[int] = None
    """Идентификатор станции метро Циан"""
    construction_date: Optional[_datetime] = None
    """Дата постройки"""
    entrances: Optional[List[UndergroundEntrance]] = None
    """Входы в метро"""
    genitive_case: Optional[str] = None
    'Название станции метро в родительном падеже (Нет Кого? Чего?)\r\nЕсли есть'
    id: Optional[int] = None
    """Идентификатор станции метро"""
    is_put_into_operation: Optional[bool] = None
    """Введён ли в экслпуатацию"""
    lat: Optional[float] = None
    """Широта"""
    lines: Optional[List[LineModel]] = None
    """Линии метро, где фигурирует станция"""
    lng: Optional[float] = None
    """Долгота"""
    location_id: Optional[int] = None
    """Id региона"""
    name: Optional[str] = None
    """Название станции метро"""
    native_name: Optional[str] = None
    'Название станции метро (оригинальное имя)\r\nЕсли есть'
    prepositional_case: Optional[str] = None
    'Названии станции метро в предложном падеже (Думать О ком? О чём?)\r\nЕсли есть'
    time_by_car: Optional[int] = None
    """Id региона"""
    time_by_walk: Optional[int] = None
    """Id региона"""
    translit_name: Optional[str] = None
    """Название станции метро в транслите"""
