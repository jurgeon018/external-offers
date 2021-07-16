from cian_core.statsd import statsd
from external_offers import pg
from external_offers.repositories.postgresql.offers import (
    get_synced_objects_count,
    get_processed_synced_objects_count,
    unsync_objects_with_grafana,
    sync_waiting_objects_with_grafana,
    get_unsynced_waiting_objects_count,
    get_segmented_objects,
)

async def send_waiting_offers_and_clients_amount_to_grafana() -> None:
    # synced_with_grafana - поле, по которому вечером определяется,
    # было ли обьявление отправлено в графану утром в статусе ожидания.

    # количество клиентов и заданий в ожидании в начале дня, которые будут отправлены в графану 
    waiting_clients_count = await get_unsynced_waiting_objects_count('clients')
    waiting_offers_count = await get_unsynced_waiting_objects_count('offers_for_call')

    # отправка метрик в графану
    statsd.incr('waiting_clients.count', count=waiting_clients_count)
    await send_segments_count_to_grafana('waiting_clients.count')

    statsd.incr( 'waiting_offers.count', count=waiting_offers_count)
    await send_segments_count_to_grafana('waiting_offers.count')

    # синхронизация клиентов с заданий с графаной(проставляем synced_with_grafana = TRUE)
    await sync_waiting_objects_with_grafana('clients')
    await sync_waiting_objects_with_grafana('offers_for_call')


async def send_processed_offers_and_clients_amount_to_grafana() -> None:
    # количество всех клиентов и заданий в ожидании, которые попали в графану утром
    synced_clients_count = await get_synced_objects_count('clients')
    synced_offers_count = await get_synced_objects_count('offers_for_call')

    # количество обработаных клиентов и заданий в конце дня.
    # обработаные - те, которые утром попали в графану в ожидании, и в течении дня их статус поменялся
    processed_synced_clients_count = await get_processed_synced_objects_count('clients')
    processed_synced_offers_count = await get_processed_synced_objects_count('offers_for_call')

    # процент обработаных клиентов и заданий в конце дня
    processed_synced_offers_percentage = await get_synced_percentage(
        synced_offers_count,
        processed_synced_offers_count
    )
    processed_synced_clients_percentage = await get_synced_percentage(
        synced_clients_count,
        processed_synced_clients_count
    )

    # отправка метрик в графану
    statsd.incr('processed_offers.count', count=processed_synced_offers_count)
    await send_segments_count_to_grafana('processed_offers.count')
    statsd.incr('processed_clients.count',count=processed_synced_clients_count)
    await send_segments_count_to_grafana('processed_clients.count')

    statsd.incr(
        'processed_clients.percentage',
        count=processed_synced_clients_percentage
    )
    await send_segments_count_to_grafana(
        'processed_clients.percentage'
    )
    statsd.incr(
        'processed_offers.percentage',
        count=processed_synced_offers_percentage
    )
    await send_segments_count_to_grafana(
        'processed_offers.percentage'
    )

    # в конце дня проставляем клиентам и заданиям synced_with_grafana = NULL
    await unsync_objects_with_grafana('clients')
    await unsync_objects_with_grafana('offers_for_call')


async def get_count(obj) -> str:
    try:
        count = get_synced_percentage(
            obj['synced_count'],
            obj['processed_synced_count'],
        )
    except KeyError:
        count = obj['count']
    return count


async def send_segments_count_to_grafana(metric: str):
    regions: list = await get_segmented_objects(metric, 'regions')
    user_segments: list = await get_segmented_objects(metric, 'user_segments')
    categories: list = await get_segmented_objects(metric, 'categories')
    print('regions:', regions)
    print('user_segments:', user_segments)
    print('categories:', categories)
    for region in regions:
        name = region['region']
        count = get_count(region)
        statsd.incr(f'{metric}.region.{name}', count=count)
    for segment in user_segments:
        name = segment['segment']
        count = get_count(segment)
        statsd.incr(f'{metric}.segment.{name}', count=count)
    for category in categories:
        name = category['category']
        count = get_count(category)
        statsd.incr(f'{metric}.category.{name}', count=count)


async def get_synced_percentage(synced_count, processed_synced_count) -> int:
    # synced_count - количество синхронизированых с графаной утром(утром они были в ожидании)
    # processed_synced_count - количество обработаных в течении дня
    if synced_count == 0 or processed_synced_count == 0:
        processed_synced_percentage = 0
    else:
        processed_synced_percentage = processed_synced_count / synced_count * 100
    return int(processed_synced_percentage)

