from typing import List

from external_offers.entities.grafana_metric import SegmentedObject
from external_offers.enums.grafana_metric import GrafanaMetric, GrafanaSegmentType
from external_offers.repositories.postgresql import fetch_segmented_objects


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
    return segmented_objects


async def get_synced_percentage(synced_count: int, processed_synced_count: int) -> int:
    """
    synced_count - количество синхронизированых с графаной утром(утром они были в ожидании)
    processed_synced_count - количество обработаных в течении дня
    """
    if synced_count == 0 or processed_synced_count == 0:
        processed_synced_percentage = 0
    else:
        processed_synced_percentage = processed_synced_count / synced_count * 100
    return int(processed_synced_percentage)


async def transform_list_into_dict(
    segmented_objects: list,
) -> dict:
    dct = {}
    for segmented_object in segmented_objects:
        key = segmented_object.segment_name
        value = segmented_object.segment_count
        dct[key] = value
    return dct
