# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-geoapi`

cian-codegen version: 1.12.2

"""
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum

from .district_direction import DistrictDirection


class Type(StrEnum):
    __value_format__ = NoFormat
    okrug = 'Okrug'
    """Округ"""
    raion = 'Raion'
    """Район"""
    mikro_raion = 'MikroRaion'
    """Микрорайон"""
    poselenie = 'Poselenie'
    """Поселение"""


@dataclass
class GetDistrictsResponse:
    """Ответ на получение районов"""

    boundaries: Optional[str] = None
    """Границы райнона"""
    direction: Optional[DistrictDirection] = None
    """Направление района"""
    full_name: Optional[str] = None
    """Полное название"""
    has_boundaries: Optional[bool] = None
    """Есть ли границы района"""
    id: Optional[int] = None
    """Id района"""
    location_full_name: Optional[str] = None
    """Полное название области"""
    location_id: Optional[int] = None
    """Ид области"""
    name: Optional[str] = None
    """Название района"""
    native_name: Optional[str] = None
    """Нативное название"""
    parent_id: Optional[int] = None
    """Ид родителя"""
    sort_order: Optional[int] = None
    """Порядковый номер"""
    translit_name: Optional[str] = None
    """Название в транслите"""
    type: Optional[Type] = None
    """Тип района"""
