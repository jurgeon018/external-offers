from typing import List, Optional

from my_offers.repositories.monolith_cian_announcementapi.entities import CalculatedUndergrounds, Geo, UndergroundInfo


def get_walking_time(geo: Optional[Geo]) -> Optional[float]:
    walking_time = None

    if not geo:
        return walking_time

    walking_time = _get_walking_time_from_calculated_undergrounds(geo.calculated_undergrounds)
    if not walking_time:
        walking_time = _get_walking_time_from_undergrounds(geo.undergrounds)

    return walking_time


def _get_walking_time_from_calculated_undergrounds(
        calculated_undergrounds: Optional[List[CalculatedUndergrounds]]
) -> Optional[float]:
    walking_time = None
    if not calculated_undergrounds:
        return walking_time

    for underground in calculated_undergrounds:
        if not underground.transport_type:
            continue
        if not underground.transport_type.is_walk:
            continue
        if not walking_time or underground.time < walking_time:
            walking_time = underground.time

    return walking_time


def _get_walking_time_from_undergrounds(undergrounds: Optional[List[UndergroundInfo]]) -> Optional[float]:
    walking_time = None
    if not undergrounds:
        return walking_time

    min_transport_time = None

    for underground in undergrounds:
        time = underground.time
        if not time:
            continue

        if not underground.transport_type:
            continue

        if underground.transport_type.is_walk:
            if not walking_time or time < walking_time:
                walking_time = time
        elif underground.transport_type.transport:
            if not min_transport_time or time < min_transport_time:
                min_transport_time = time

    if not walking_time and min_transport_time:
        # здесь умножаем на 10, потому что если человек идет
        # со срденей скоростью 4 км/ч, то автомобиль со скоростью 40 км/ч(в шарпе такие константы)
        # что в 10 раз больше
        # 2015 год python-monolith
        walking_time = min_transport_time * 10

    return walking_time
