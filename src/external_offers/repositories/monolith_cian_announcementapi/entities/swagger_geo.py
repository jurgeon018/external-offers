# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import List, Optional

from .address_info import AddressInfo
from .calculated_undergrounds import CalculatedUndergrounds
from .coordinates import Coordinates
from .district_info import DistrictInfo
from .highway_info import HighwayInfo
from .jk import Jk
from .location_path import LocationPath
from .railway_info import RailwayInfo
from .underground_info import UndergroundInfo


@dataclass
class SwaggerGeo:
    address: Optional[List[AddressInfo]] = None
    """Адресный элемент"""
    building_address: Optional[str] = None
    """Строительный адрес"""
    calculated_undergrounds: Optional[List[CalculatedUndergrounds]] = None
    """Автоматически рассчитанное время в пути до метро"""
    coordinates: Optional[Coordinates] = None
    """Координаты точки (пользовательского пина на карте)"""
    country_id: Optional[int] = None
    """ID страны"""
    district: Optional[List[DistrictInfo]] = None
    """Район"""
    highways: Optional[List[HighwayInfo]] = None
    """Шоссе"""
    jk: Optional[Jk] = None
    """ЖК"""
    location_path: Optional[LocationPath] = None
    """LocationPath"""
    publish_coordinates: Optional[Coordinates] = None
    """Координаты, в которых опубликовано объявление."""
    railways: Optional[List[RailwayInfo]] = None
    """Жд станции"""
    undergrounds: Optional[List[UndergroundInfo]] = None
    """Метро"""
    user_input: Optional[str] = None
    """Адресная строка, введенная пользователем"""
