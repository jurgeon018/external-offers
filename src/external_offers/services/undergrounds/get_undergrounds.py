"""
Скопировано из монолита cian.addform.service.get_underground_by_coordinates
"""

from typing import List

from cian_cache import CachedOptions, cached
from simple_settings import settings

from external_offers.repositories.monolith_cian_announcementapi.entities import Coordinates, UndergroundInfo
from external_offers.repositories.monolith_cian_announcementapi.entities.calculated_undergrounds import TransportType
from external_offers.repositories.monolith_cian_geoapi import v2_undergrounds_get_all
from external_offers.repositories.monolith_cian_geoapi.entities import UndergroundModelV2
from external_offers.repositories.monolith_cian_realty import api_autocomplete_undeground
from external_offers.repositories.monolith_cian_realty.entities import ApiAutocompleteUndeground
from external_offers.services.undergrounds.utils import haversine


async def get_all_undergrounds() -> List[UndergroundModelV2]:
    return await v2_undergrounds_get_all()


get_all_undergrounds_cached = cached(
    group='external_offers_get_all_undergrounds',
    options=CachedOptions(
        ttl=settings.GET_ALL_UNDERGROUNDS_CACHE_TTL,
        use_global_cache=False,
        use_local_cache=True,
    )
)(get_all_undergrounds)


async def get_underground_by_coordinates(
    *,
    coordinates: Coordinates,
    region_id: int
) -> List[UndergroundInfo]:
    undergrounds: List[UndergroundInfo] = []
    radius = settings.UNDERGROUND_SEARCH_RADIUS
    # не использовать region_id для фильтрации так как объекты в МО
    # расположенные близко к метро не будут учитываться
    all_metro = await get_all_undergrounds_cached()
    calculate_distance_within_radius = {}
    for metro in all_metro:
        distance = haversine(
            lon1=metro.lng,
            lat1=metro.lat,
            lon2=coordinates.lng,
            lat2=coordinates.lat
        )
        if distance > radius:
            continue

        calculate_distance_within_radius[metro.name] = distance
    underground_addresses = sorted(
        calculate_distance_within_radius, key=lambda metro_name: calculate_distance_within_radius[metro_name]
    )[:settings.MAX_GEOCODE_STATIONS]

    if underground_addresses:
        underground_names = set()
        skip_count = 0
        for underground_address in underground_addresses:
            station_name = underground_address.replace('метро ', '').replace('станция ', '')
            if station_name in underground_names:
                skip_count += 1
                continue

            results = await api_autocomplete_undeground(
                ApiAutocompleteUndeground(
                    region_id=region_id,
                    q=station_name,
                    lng=coordinates.lng,
                    lat=coordinates.lat,
                )
            )
            if results:
                result = results[0]
                transport_type = None
                time = None
                if result.time_by_walk:
                    time = result.time_by_walk
                    transport_type = TransportType.walk
                elif result.time_by_car:
                    time = result.time_by_car
                    transport_type = TransportType.transport

                undergrounds.append(
                    UndergroundInfo(
                        cian_id=result.id,
                        id=None,
                        is_default=True,
                        line_color=result.color,
                        line_id=result.id,
                        name=result.name,
                        time=time,
                        transport_type=transport_type
                    )
                )
                underground_names.add(results[0].name)

    return undergrounds
