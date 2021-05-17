
from typing import List

from cian_cache import CachedOptions, cached
from cian_core.runtime_settings import runtime_settings
from cian_http.exceptions import ApiClientException

from external_offers.repositories.monolith_cian_geoapi import v1_get_districts_by_child, v1_get_districts_by_ids
from external_offers.repositories.monolith_cian_geoapi.entities import GetDistrictsResponse, V1GetDistrictsByChild, V1GetDistrictsByIds
from external_offers.repositories.monolith_cian_geoapi.entities.v1_get_districts_by_child import GeoType
from external_offers.services.districts.exceptions import GetDistrictsByHouseError


async def get_districts_by_house_id(
    *,
    house_id: int
) -> List[GetDistrictsResponse]:
    try:
        return await v1_get_districts_by_child(
            V1GetDistrictsByChild(
                id=house_id,
                geo_object_type=GeoType.house,
            )
        )
    except ApiClientException as exc:
        raise GetDistrictsByHouseError from exc

get_districts_by_house_id_cached = cached(
    group='external_offers_get_districts_by_house_id',
    options=CachedOptions(
        ttl=runtime_settings.GET_DISTRICTS_BY_HOUSE_CACHE_TTL,
        use_global_cache=False,
        use_local_cache=True,
    )
)(get_districts_by_house_id)


async def get_districts_by_district_ids(
    *,
    ids: List[int]
) -> List[GetDistrictsResponse]:
    try:
        return await v1_get_districts_by_ids(
            V1GetDistrictsByIds(
                ids=ids,
            )
        )
    except ApiClientException as exc:
        raise GetDistrictsByHouseError from exc

get_districts_by_district_ids_cached = cached(
    group='external_offers_get_districts_by_ids',
    options=CachedOptions(
        ttl=runtime_settings.GET_DISTRICTS_BY_IDS_CACHE_TTL,
        use_global_cache=False,
        use_local_cache=True,
    )
)(get_districts_by_district_ids)
