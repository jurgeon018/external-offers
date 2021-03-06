# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-geoapi`

cian-codegen version: 1.16.3

"""
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


class GeoType(StrEnum):
    __value_format__ = NoFormat
    country = 'Country'
    """Страна"""
    location = 'Location'
    """Локация"""
    street = 'Street'
    """Улица"""
    road = 'Road'
    """Шоссе"""
    district = 'District'
    """Район"""
    underground = 'Underground'
    """Метро"""
    house = 'House'
    """Дом"""
    entry_into_road = 'EntryIntoRoad'
    """Въезд на шоссе"""
    new_object = 'NewObject'
    """ЖК - новостройки"""


@dataclass
class Details:
    """Содержит в себе массив объектов, каждый из которых описывает часть адреса (то что разделено запятыми)."""

    full_name: Optional[str] = None
    'Полное название адресного элемента. \r\nТ.е. вместе с указанием типа объекта, например, площадь Ленина, деревня Ново).'
    geo_type: Optional[GeoType] = None
    """Тип адресного элемента (страна, локация, улица, дом)."""
    has_metro: Optional[bool] = None
    """Есть метро."""
    has_road: Optional[bool] = None
    """Есть шоссе."""
    id: Optional[int] = None
    """Идентификатор в нашей базе."""
    is_locality: Optional[bool] = None
    """Если населенный пункт."""
    name: Optional[str] = None
    """Короткое название адресного элемента."""
    street_required: Optional[bool] = None
    """Если улица обязательна."""
