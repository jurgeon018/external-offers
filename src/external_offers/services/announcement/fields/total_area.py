from typing import Optional

from my_offers.repositories.monolith_cian_announcementapi.entities import Land
from my_offers.services.announcement.helpers.units import area_to_meters_kf


def get_total_area(*, total_area: Optional[float], land: Optional[Land]) -> Optional[float]:
    if total_area:
        return total_area

    if not land:
        return None

    result = land.area
    if not result:
        return None

    unit_type = land.area_unit_type
    if unit_type:
        result *= area_to_meters_kf(unit_type)

    return round(result, 2)
