from cian_core.statsd import statsd
from external_offers import pg
from external_offers.entities.grafana_metric import SegmentedObject
from external_offers.repositories.postgresql.offers import (
    get_synced_objects_count,
    get_processed_synced_objects_count,
    unsync_objects_with_grafana,
    sync_waiting_objects_with_grafana,
    get_unsynced_waiting_objects_count,
)
from external_offers.enums.grafana_metric import GrafanaMetric, GrafanaSegmentType
from external_offers.services.grafana_metric import (
    get_segmented_objects,
    get_synced_percentage,
)


async def send_segments_count_to_grafana(metric: GrafanaMetric):
    regions = await get_segmented_objects(metric, GrafanaSegmentType.region)
    user_segments = await get_segmented_objects(metric, GrafanaSegmentType.user_segment)
    categories = await get_segmented_objects(metric, GrafanaSegmentType.category)
    # print()
    # print('----------------------------')
    # print('metric: ', metric)
    # print('regions:', regions)
    # print('user_segments:', user_segments)
    # print('categories:', categories)
    # print('----------------------------')
    # print()
    for region in regions:
        statsd.incr(
            f'{metric}.{GrafanaSegmentType.region}.{region.segment_name}', 
            count=region.segment_count
        )
    for user_segment in user_segments:
        statsd.incr(
            f'{metric}.{GrafanaSegmentType.user_segment}.{user_segment.segment_name}', 
            count=user_segment.segment_count
        )
    for category in categories:
        statsd.incr(
            f'{metric}.{GrafanaSegmentType.category}.{category.segment_name}', 
            count=category.segment_count
        )


async def send_waiting_offers_and_clients_amount_to_grafana() -> None:
    # synced_with_grafana - поле, по которому вечером определяется,
    # было ли обьявление отправлено в графану утром в статусе ожидания.
    
    waiting_clients_count = await get_unsynced_waiting_objects_count('clients')
    waiting_offers_count = await get_unsynced_waiting_objects_count('offers_for_call')

    print('-----------')
    print('waiting_clients_count:', waiting_clients_count)
    print('waiting_offers_count:', waiting_offers_count)

    # отправка метрик в графану
    statsd.incr(GrafanaMetric.waiting_clients_count, count=waiting_clients_count)
    await send_segments_count_to_grafana(GrafanaMetric.waiting_clients_count)

    statsd.incr(GrafanaMetric.waiting_offers_count, count=waiting_offers_count)
    await send_segments_count_to_grafana(GrafanaMetric.waiting_offers_count)

    print('-----------')

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
    print('--------------')
    print("synced_clients_count:", synced_clients_count)
    print("synced_offers_count:", synced_offers_count)
    print("processed_synced_clients_count:", processed_synced_clients_count)
    print("processed_synced_offers_count:", processed_synced_offers_count)
    print("processed_offers_percentage:", processed_offers_percentage)
    print("processed_synced_clients_percentage:", processed_synced_clients_percentage)
    # отправка метрик в графану
    statsd.incr(GrafanaMetric.processed_offers_count, count=processed_synced_offers_count)
    await send_segments_count_to_grafana(GrafanaMetric.processed_offers_count)
    statsd.incr(GrafanaMetric.processed_clients_count,count=processed_synced_clients_count)
    await send_segments_count_to_grafana(GrafanaMetric.processed_clients_count)

    statsd.incr(
        GrafanaMetric.processed_clients_percentage,
        count=processed_synced_clients_percentage
    )
    await send_segments_count_to_grafana(
        GrafanaMetric.processed_clients_percentage
    )
    statsd.incr(
        GrafanaMetric.processed_offers_percentage,
        count=processed_offers_percentage
    )
    await send_segments_count_to_grafana(
        GrafanaMetric.processed_offers_percentage
    )
    print('--------------')

    # в конце дня проставляем клиентам и заданиям synced_with_grafana = NULL
    await unsync_objects_with_grafana('clients')
    await unsync_objects_with_grafana('offers_for_call')
