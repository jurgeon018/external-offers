import logging
from typing import List, Optional

from cian_http.exceptions import ApiClientException
from pytils import translit

from external_offers.entities.exceptions import NotFoundRegionNameException
from external_offers.entities.grafana_metric import SegmentedObject
from external_offers.enums.grafana_metric import GrafanaMetric, GrafanaSegmentType
from external_offers.helpers.region_names import REGION_NAMES
from external_offers.repositories.monolith_cian_geoapi import v1_locations_get
from external_offers.repositories.monolith_cian_geoapi.entities import V1LocationsGet
from external_offers.repositories.postgresql import fetch_segmented_objects


logger = logging.getLogger(__name__)


count_metrics = [
    GrafanaMetric.waiting_offers_count,
    GrafanaMetric.waiting_clients_count,
    GrafanaMetric.processed_offers_count,
    GrafanaMetric.processed_clients_count,
]
percentage_metrics = [
    GrafanaMetric.processed_clients_percentage,
    GrafanaMetric.processed_offers_percentage,
]


async def get_segmented_objects(
    metric: GrafanaMetric,
    segment_type: GrafanaSegmentType,
) -> List[SegmentedObject]:
    if metric in count_metrics:
        segmented_objects = await fetch_segmented_objects(segment_type, metric)
    elif metric in percentage_metrics:
        all_synced_count: dict = await transform_list_into_dict(
            await fetch_segmented_objects(segment_type, metric, processed=False)
        )
        processed_synced_count: dict = await transform_list_into_dict(
            await fetch_segmented_objects(segment_type, metric, processed=True)
        )
        # превращение списка сегментированых обьектов в словарь делается для того,
        # чтобы можно было по ключу с названием сегмента
        # достать количество обработаных обьектов из словаря с обработаными обьектами,
        # что позволяет обойтись без вложеных циклов.
        segmented_objects = [
            SegmentedObject(
                segment_name=name,
                segment_count=await get_synced_percentage(
                    count,
                    processed_synced_count.get(name, 0)
                )
            ) for name, count in all_synced_count.items()
        ]
    if segment_type == GrafanaSegmentType.region:
        segmented_objects = await map_region_codes_to_region_names(segmented_objects)
    return segmented_objects


async def get_synced_percentage(synced_count: int, processed_synced_count: int) -> int:
    """
    synced_count - количество синхронизированых с графаной утром(утром они были в ожидании)
    processed_synced_count - количество обработаных в течении дня
    """
    if synced_count == 0 or processed_synced_count == 0:
        return 0
    else:
        return int(processed_synced_count / synced_count * 100)


async def transform_list_into_dict(
    segmented_objects: list,
) -> dict:
    dct = {}
    for segmented_object in segmented_objects:
        key = segmented_object.segment_name
        value = segmented_object.segment_count
        dct[key] = value
    return dct


async def map_region_codes_to_region_names(
    segmented_regions: List[SegmentedObject]
) -> List[SegmentedObject]:
    mapped_segmented_regions = []
    for segmented_region in segmented_regions:
        region_id = segmented_region.segment_name
        region_name = await get_region_name(region_id)
        segment_name = f'{region_name}_{region_id}'
        mapped_segmented_regions.append(
            SegmentedObject(
                   segment_name=segment_name,
                   segment_count=segmented_region.segment_count,
            )
        )
    return mapped_segmented_regions


async def get_region_name(region_id: str) -> Optional[str]:
    region_name = await get_region_name_from_dict(region_id)
    if not region_name:
        region_name = await get_region_name_from_api(region_id)
    if not region_name:
        raise NotFoundRegionNameException(f'Название региона по id {region_id} небыло найдено.')
    region_name = translit.slugify(region_name)
    return region_name


async def get_region_name_from_api(region_id: str) -> Optional[str]:
    try:
        response = await v1_locations_get(
            V1LocationsGet(id=int(region_id)),
        )
        region_name = response.name
    except ApiClientException as exc:
        logger.warning(
            'Название региона по коду %s небыло найдено в ручке /v1/locations/get/. %s',
            region_id,
            exc,
        )
        region_name = None
    return region_name


async def get_region_name_from_dict(region_id: str) -> Optional[str]:
    try:
        return REGION_NAMES[region_id]
    except KeyError:
        logger.warning(
            'Название региона по коду %s небыло найдено в файле с регионами.',
            region_id,
        )
        return None
