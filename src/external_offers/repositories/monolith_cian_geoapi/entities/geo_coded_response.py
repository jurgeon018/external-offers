# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-geoapi`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import List, Optional

from .details import Details
from .geo import Geo


@dataclass
class GeoCodedResponse:
    billing_region_id: Optional[int] = None
    """Идентификатор региона тарифной сетки."""
    country_id: Optional[int] = None
    """ID страны"""
    details: Optional[List[Details]] = None
    """Содержит в себе массив объектов, каждый из которых описывает часть адреса (то что разделено запятыми)."""
    geo: Optional[Geo] = None
    """Информация по Гео (широта, долгота)."""
    is_parsed: Optional[bool] = None
    """Если удалось распарсить адрес."""
    location_path: Optional[List[int]] = None
    'Идентификаторы всех локаций, от родительского до самого точного\r\nИспользуется в биллинге'
    postal_code: Optional[str] = None
    """Почтовый индекс"""
    text: Optional[str] = None
    """Результат яндекса после геокодинга."""