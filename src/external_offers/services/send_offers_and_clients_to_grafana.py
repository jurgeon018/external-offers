from cian_core.statsd import statsd
from external_offers import pg
from external_offers.repositories.postgresql.offers import (
    get_synced_offers_count,
    get_synced_clients_count,
    get_non_waiting_synced_offers_count,
    get_non_waiting_synced_clients_count,
    unsync_clients_with_grafana,
    unsync_offers_with_grafana,
    sync_waiting_clients_with_grafana,
    sync_waiting_offers_with_grafana,
)

# TODO: сегментировать:

async def send_waiting_offers_and_clients_amount_to_grafana():
    # количество клиентов и заданий в ожидании в начале дня, которые будут отправлены в графану 
    waiting_clients_count = await sync_waiting_clients_with_grafana()
    waiting_offers_count = await sync_waiting_offers_with_grafana()
    # отправка метрик в графану
    await send_segments_to_grafana('waiting_clients', count=waiting_clients_count)
    await send_segments_to_grafana('waiting_offers', count=waiting_offers_count)


async def send_non_waiting_offers_and_clients_amount_to_grafana():

    # количество всех клиентов и заданий в ожидании, которые попали в графану утром
    synced_clients_count = await get_synced_clients_count()
    synced_offers_count = await get_synced_offers_count()

    # количество обработаных клиентов и заданий в конце дня.
    # обработаные - те, которые утром попали в графану в ожидании, и в течении дня их статус поменялся)
    non_waiting_synced_clients_count = await get_non_waiting_synced_clients_count()
    non_waiting_synced_offers_count = await get_non_waiting_synced_offers_count()

    # процент обработаных клиентов и заданий в конце дня
    non_waiting_synced_offers_percentage = await get_synced_percentage(synced_offers_count, non_waiting_synced_offers_count)
    non_waiting_synced_clients_percentage = await get_synced_percentage(synced_clients_count, non_waiting_synced_clients_count)

    # отправка метрик в графану
    await send_segments_to_grafana('non_waiting_offers', count=non_waiting_synced_offers_count)
    await send_segments_to_grafana('non_waiting_clients', count=non_waiting_synced_clients_count)
    statsd.incr(f'non_waiting_clients.percentage', count=non_waiting_synced_clients_percentage)
    statsd.incr(f'non_waiting_offers.percentage', count=non_waiting_synced_offers_percentage)

    # проставляем клиентам и заданиям synced_with_grafana = NULL
    await unsync_clients_with_grafana()
    await unsync_offers_with_grafana()


async def send_segments_to_grafana(key, count, rate=1):
    statsd.incr(f'{key}.count', count=count)
    # for segmented_key, segmented_count in get_segmentation(key).items():
    #     statsd.incr(segmented_key, count=segmented_count, rate=rate)


async def get_segmentation(key):
    result = {}
    regions = await get_regions(key)
    segments = await get_segments(key)
    categories = await get_categories(key)
    for region in regions:
        region_name = region['region']
        region_count = region['count']
        result[f'{key}.count.region_{region_name}'] = region_count
    for segment in segments:
        segment_name = segment['segment']
        segment_count = segment['count']
        result[f'{key}.count.segment_{segment_name}'] = segment_count
    for category in categories:
        category_name = category['segment']
        category_count = category['count']
        result[f'{key}.count.category_{category_name}'] = category_count
    return result


async def get_synced_percentage(synced_count, non_waiting_synced_count):
    # synced_count - количество в ожидании утром
    # non_waiting_synced_count - количество обработаных в течении дня
    if synced_count == 0 or non_waiting_synced_count == 0:
        non_waiting_synced_percentage = 0
    else:
        non_waiting_synced_percentage = non_waiting_synced_count / synced_count * 100
    return int(non_waiting_synced_percentage)


async def get_regions(key):
    default_regions_query = """
        SELECT source_object_model->'region', COUNT(source_object_model->'region')
        FROM parsed_offers
        WHERE id IN (
            SELECT parsed_id FROM offers_for_call
        )
        GROUP BY source_object_model->'region';
    """
    if key == 'waiting_clients':
        regions = 'TODO ...'
    elif key == 'waiting_offers':
        regions = 'TODO ...'
    elif key == 'non_waiting_offers':
        regions = 'TODO ...'
    elif key == 'non_waiting_clients':
        regions = 'TODO ...'
    return regions 


async def get_segments(key):
    default_segments_query = """
        SELECT user_segment, COUNT(user_segment)
        FROM parsed_offers
        WHERE id IN (
            SELECT parsed_id FROM offers_for_call
        )
        GROUP BY user_segment;
    """
    if key == 'waiting_clients':
        segments = 'TODO ...'
    elif key == 'waiting_offers':
        segments = 'TODO ...'
    elif key == 'non_waiting_offers':
        segments = 'TODO ...'
    elif key == 'non_waiting_clients':
        segments = 'TODO ...'
    return segments 


async def get_categories(key):
    default_categories_query = """
        SELECT category, COUNT(category)
        FROM offers_for_call
        GROUP BY category;
    """
    if key == 'waiting_clients':
        categories = 'TODO ...'
    elif key == 'waiting_offers':
        categories = 'TODO ...'
    elif key == 'non_waiting_offers':
        categories = 'TODO ...'
    elif key == 'non_waiting_clients':
        categories = 'TODO ...'
    return categories 
