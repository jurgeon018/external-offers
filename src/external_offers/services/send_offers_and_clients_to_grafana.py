from cian_core.statsd import statsd

from external_offers.enums.grafana_metric import GrafanaMetric, GrafanaSegmentType
from external_offers.repositories.postgresql.grafana_objects import (
    get_processed_synced_objects_count,
    get_synced_objects_count,
    get_unsynced_waiting_objects_count,
    sync_waiting_objects_with_grafana,
    unsync_objects_with_grafana,
)
from external_offers.services.grafana_metric import get_segmented_objects, get_synced_percentage


async def send_segments_count_to_grafana(metric: GrafanaMetric) -> None:
    segment_types = [
        GrafanaSegmentType.region,
        GrafanaSegmentType.user_segment,
        GrafanaSegmentType.category,
    ]
    for segment_type in segment_types:
        segmented_objects = await get_segmented_objects(metric, segment_type)
        for segmented_object in segmented_objects:
            statsd.incr(
                f'{metric.value}.{segment_type}.{segmented_object.segment_name}',
                count=segmented_object.segment_count
            )


async def send_waiting_offers_and_clients_amount_to_grafana() -> None:
    # synced_with_grafana - поле, по которому вечером определяется,
    # было ли обьявление отправлено в графану утром в статусе ожидания.

    waiting_clients_count = await get_unsynced_waiting_objects_count('clients')
    waiting_offers_count = await get_unsynced_waiting_objects_count('offers_for_call')

    # отправка метрик в графану
    statsd.incr(GrafanaMetric.waiting_clients_count.value, count=waiting_clients_count)
    await send_segments_count_to_grafana(GrafanaMetric.waiting_clients_count)

    statsd.incr(GrafanaMetric.waiting_offers_count.value, count=waiting_offers_count)
    await send_segments_count_to_grafana(GrafanaMetric.waiting_offers_count)

    # синхронизация клиентов с заданий с графаной(проставляем synced_with_grafana = TRUE)
    await sync_waiting_objects_with_grafana('clients')
    await sync_waiting_objects_with_grafana('offers_for_call')


async def send_processed_offers_and_clients_amount_to_grafana() -> None:
    # количество всех клиентов и заданий в ожидании, которые попали в графану утром
    synced_clients_count = await get_synced_objects_count('clients')
    synced_offers_count = await get_synced_objects_count('offers_for_call')

    # количество обработаных клиентов и заданий в конце дня
    processed_synced_clients_count = await get_processed_synced_objects_count('clients')
    processed_synced_offers_count = await get_processed_synced_objects_count('offers_for_call')

    # процент обработаных клиентов и заданий в конце дня
    processed_offers_percentage = await get_synced_percentage(
        synced_offers_count,
        processed_synced_offers_count
    )
    processed_synced_clients_percentage = await get_synced_percentage(
        synced_clients_count,
        processed_synced_clients_count
    )
    # отправка метрик в графану
    statsd.incr(GrafanaMetric.processed_offers_count.value, count=processed_synced_offers_count)
    await send_segments_count_to_grafana(GrafanaMetric.processed_offers_count)
    statsd.incr(GrafanaMetric.processed_clients_count.value, count=processed_synced_clients_count)
    await send_segments_count_to_grafana(GrafanaMetric.processed_clients_count)

    statsd.incr(
        GrafanaMetric.processed_clients_percentage.value,
        count=processed_synced_clients_percentage
    )
    await send_segments_count_to_grafana(GrafanaMetric.processed_clients_percentage)
    statsd.incr(
        GrafanaMetric.processed_offers_percentage.value,
        count=processed_offers_percentage
    )
    await send_segments_count_to_grafana(GrafanaMetric.processed_offers_percentage)

    # в конце дня проставляем клиентам и заданиям synced_with_grafana = NULL
    await unsync_objects_with_grafana('clients')
    await unsync_objects_with_grafana('offers_for_call')
