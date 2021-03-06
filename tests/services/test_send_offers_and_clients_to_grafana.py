import pytest
from cian_http.exceptions import ApiClientException
from cian_test_utils import future

from external_offers.entities.exceptions import NotFoundRegionNameException
from external_offers.entities.grafana_metric import SegmentedObject
from external_offers.enums.grafana_metric import GrafanaMetric, GrafanaSegmentType
from external_offers.repositories.monolith_cian_geoapi.entities import LocationResponse, V1LocationsGet
from external_offers.services.grafana_metric import (
    get_region_name,
    get_region_name_from_api,
    get_segmented_objects,
    get_synced_percentage,
    map_region_codes_to_region_names,
    transform_list_into_dict,
)
from external_offers.services.send_offers_and_clients_to_grafana import (
    send_processed_offers_and_clients_amount_to_grafana,
    send_segments_count_to_grafana,
    send_waiting_offers_and_clients_amount_to_grafana,
)


# external_offers.services.send_offers_and_clients_to_grafana

@pytest.mark.parametrize('metric', [
    GrafanaMetric.waiting_offers_count,
    GrafanaMetric.waiting_clients_count,
    GrafanaMetric.processed_offers_count,
    GrafanaMetric.processed_clients_count,
    GrafanaMetric.processed_clients_percentage,
    GrafanaMetric.processed_offers_percentage,
])
async def test_send_segments_count_to_grafana(mocker, metric):
    segmented_objects = future([
        SegmentedObject(segment_name='name1', segment_count=1),
        SegmentedObject(segment_name='name2', segment_count=7),
        SegmentedObject(segment_name='name3', segment_count=3),
    ])
    segment_types = [
        GrafanaSegmentType.region,
        GrafanaSegmentType.user_segment,
        GrafanaSegmentType.category,
    ]
    get_segmented_objects_mock = mocker.patch(
        'external_offers.services.'
        'send_offers_and_clients_to_grafana.get_segmented_objects'
    )
    get_segmented_objects_mock.return_value = segmented_objects
    statsd_incr_mock = mocker.patch(
        'external_offers.services.'
        'send_offers_and_clients_to_grafana.statsd.incr'
    )
    await send_segments_count_to_grafana(metric)
    statsd_incr_calls = []
    get_segmented_objects_calls = []
    for segment_type in segment_types:
        get_segmented_objects_calls.append(mocker.call(metric, segment_type))
        for segmented_object in segmented_objects:
            statsd_incr_mock.append(mocker.call(
                f'{metric}.{segment_type}.{segmented_object.segment_name}',
                count=segmented_object.segment_count
            ))
    get_segmented_objects_mock.assert_has_calls(get_segmented_objects_calls)
    statsd_incr_mock.assert_has_calls(statsd_incr_calls)


async def test_send_waiting_offers_and_clients_amount_to_grafana(mocker):
    unsynced_waiting_clients_count = 10
    unsynced_waiting_offers_count = 10
    side_effect = [
        future(unsynced_waiting_clients_count),
        future(unsynced_waiting_offers_count),
    ]
    send_segments_count_to_grafana_mock = mocker.patch(
        ('external_offers.services.send_offers_and_clients_to_grafana.'
            'send_segments_count_to_grafana'),
        return_value=future(None),
    )
    get_unsynced_waiting_objects_count_mock = mocker.patch(
        ('external_offers.services.send_offers_and_clients_to_grafana.'
            'get_unsynced_waiting_objects_count'),
        side_effect=side_effect,
    )
    sync_waiting_objects_with_grafana_mock = mocker.patch(
        ('external_offers.services.send_offers_and_clients_to_grafana.'
            'sync_waiting_objects_with_grafana'),
        return_value=future(None),
    )
    statsd_mock = mocker.patch(
        ('external_offers.services.'
            'send_offers_and_clients_to_grafana.statsd.incr'),
        return_value=future(None),
    )

    await send_waiting_offers_and_clients_amount_to_grafana()

    get_unsynced_waiting_objects_count_mock.assert_has_calls([
        mocker.call('clients'),
        mocker.call('offers_for_call'),
    ])
    statsd_mock.assert_has_calls([
        mocker.call(GrafanaMetric.waiting_clients_count.value, count=unsynced_waiting_clients_count),
        mocker.call(GrafanaMetric.waiting_offers_count.value, count=unsynced_waiting_offers_count),
    ])
    send_segments_count_to_grafana_mock.assert_has_calls([
        mocker.call(GrafanaMetric.waiting_clients_count),
        mocker.call(GrafanaMetric.waiting_offers_count),
    ])
    sync_waiting_objects_with_grafana_mock.assert_has_calls([
        mocker.call('clients'),
        mocker.call('offers_for_call'),
    ])


async def test_send_processed_offers_and_clients_amount_to_grafana(mocker):
    synced_clients_count = 12
    synced_offers_count = 24
    synced_objects = [
        future(synced_clients_count),
        future(synced_offers_count),
    ]
    processed_synced_clients_count = 3
    processed_synced_offers_count = 12
    processed_synced_clients_percentage = 25  # 3 / 12 * 100
    processed_offers_percentage = 50  # 12 / 24 * 100
    processed_objects = [
        future(processed_synced_clients_count),
        future(processed_synced_offers_count),
    ]
    get_synced_objects_count_mock = mocker.patch(
        ('external_offers.services.send_offers_and_clients_to_grafana'
            '.get_synced_objects_count'),
        side_effect=synced_objects,
    )
    get_processed_synced_objects_count_mock = mocker.patch(
        ('external_offers.services.send_offers_and_clients_to_grafana'
            '.get_processed_synced_objects_count'),
        side_effect=processed_objects,
    )
    statsd_incr_mock = mocker.patch(
        ('external_offers.services.send_offers_and_clients_to_grafana'
            '.statsd.incr'),
        return_value=future(None),
    )
    send_segments_count_to_grafana_mock = mocker.patch(
        ('external_offers.services.send_offers_and_clients_to_grafana'
            '.send_segments_count_to_grafana'),
        return_value=future(None),
    )
    unsync_objects_with_grafana_mock = mocker.patch(
        ('external_offers.services.send_offers_and_clients_to_grafana'
            '.unsync_objects_with_grafana'),
        return_value=future(None),
    )
    await send_processed_offers_and_clients_amount_to_grafana()
    get_synced_objects_count_mock.assert_has_calls([
        mocker.call('clients'),
        mocker.call('offers_for_call'),
    ])
    get_processed_synced_objects_count_mock.assert_has_calls([
        mocker.call('clients'),
        mocker.call('offers_for_call'),
    ])
    statsd_incr_mock.assert_has_calls([
        mocker.call(
            GrafanaMetric.processed_offers_count.value,
            count=processed_synced_offers_count
        ),
        mocker.call(
            GrafanaMetric.processed_clients_count.value,
            count=processed_synced_clients_count
        ),
        mocker.call(
            GrafanaMetric.processed_clients_percentage.value,
            count=processed_synced_clients_percentage
        ),
        mocker.call(
            GrafanaMetric.processed_offers_percentage.value,
            count=processed_offers_percentage
        ),
    ])
    send_segments_count_to_grafana_mock.assert_has_calls([
        mocker.call(GrafanaMetric.processed_offers_count),
        mocker.call(GrafanaMetric.processed_clients_count),
        mocker.call(GrafanaMetric.processed_clients_percentage),
        mocker.call(GrafanaMetric.processed_offers_percentage),
    ])
    unsync_objects_with_grafana_mock.assert_has_calls([
        mocker.call('clients'),
        mocker.call('offers_for_call'),
    ])


# external_offers.services.grafana_metric

@pytest.mark.parametrize('metric, segment_type', [
    (GrafanaMetric.waiting_offers_count, GrafanaSegmentType.category),
    (GrafanaMetric.waiting_clients_count, GrafanaSegmentType.category),
    (GrafanaMetric.processed_offers_count, GrafanaSegmentType.category),
    (GrafanaMetric.processed_clients_count, GrafanaSegmentType.category),
    (GrafanaMetric.waiting_offers_count, GrafanaSegmentType.region),
    (GrafanaMetric.waiting_clients_count, GrafanaSegmentType.region),
    (GrafanaMetric.processed_offers_count, GrafanaSegmentType.region),
    (GrafanaMetric.processed_clients_count, GrafanaSegmentType.region),
    (GrafanaMetric.waiting_offers_count, GrafanaSegmentType.user_segment),
    (GrafanaMetric.waiting_clients_count, GrafanaSegmentType.user_segment),
    (GrafanaMetric.processed_offers_count, GrafanaSegmentType.user_segment),
    (GrafanaMetric.processed_clients_count, GrafanaSegmentType.user_segment),
])
async def test_get_segmented_counts(mocker, metric, segment_type):
    segmented_objects = [
        SegmentedObject(segment_name='4568', segment_count=10),
        SegmentedObject(segment_name='4636', segment_count=20),
        SegmentedObject(segment_name='4624', segment_count=30),
        SegmentedObject(segment_name='4590', segment_count=40),
    ]
    if segment_type == GrafanaSegmentType.region:
        expected_segmented_objects = [
            SegmentedObject(segment_name='respublika-dagestan_4568', segment_count=10),
            SegmentedObject(segment_name='yaroslavskaya-oblast_4636', segment_count=20),
            SegmentedObject(segment_name='udmurtskaya-respublika_4624', segment_count=30),
            SegmentedObject(segment_name='magadanskaya-oblast_4590', segment_count=40),
        ]
    else:
        expected_segmented_objects = [
            SegmentedObject(segment_name='4568', segment_count=10),
            SegmentedObject(segment_name='4636', segment_count=20),
            SegmentedObject(segment_name='4624', segment_count=30),
            SegmentedObject(segment_name='4590', segment_count=40),
        ]

    fetch_segmented_objects = mocker.patch(
        'external_offers.services.grafana_metric.'
        'fetch_segmented_objects',
    )
    fetch_segmented_objects.return_value = future(segmented_objects)
    result = await get_segmented_objects(metric, segment_type)

    assert result == expected_segmented_objects
    fetch_segmented_objects.assert_called_once_with(segment_type=segment_type, metric=metric)


@pytest.mark.parametrize('metric, segment_type', [
    (GrafanaMetric.processed_clients_percentage, GrafanaSegmentType.category),
    (GrafanaMetric.processed_offers_percentage, GrafanaSegmentType.category),
    (GrafanaMetric.processed_clients_percentage, GrafanaSegmentType.user_segment),
    (GrafanaMetric.processed_offers_percentage, GrafanaSegmentType.user_segment),
    (GrafanaMetric.processed_clients_percentage, GrafanaSegmentType.region),
    (GrafanaMetric.processed_offers_percentage, GrafanaSegmentType.region),
])
async def test_get_segmented_percents(mocker, metric, segment_type):
    all_synced_count = [
        SegmentedObject(segment_name='4568', segment_count=10),
        SegmentedObject(segment_name='4636', segment_count=20),
        SegmentedObject(segment_name='4624', segment_count=30),
        SegmentedObject(segment_name='4590', segment_count=40),
    ]
    processed_synced_count = [
        SegmentedObject(segment_name='4568', segment_count=0),
        SegmentedObject(segment_name='4636', segment_count=10),
        SegmentedObject(segment_name='4624', segment_count=30),
    ]
    if segment_type == GrafanaSegmentType.region:
        expected_segmented_percents = [
            SegmentedObject(segment_name='respublika-dagestan_4568', segment_count=0),
            SegmentedObject(segment_name='yaroslavskaya-oblast_4636', segment_count=50),
            SegmentedObject(segment_name='udmurtskaya-respublika_4624', segment_count=100),
            SegmentedObject(segment_name='magadanskaya-oblast_4590', segment_count=0),
        ]
    else:
        expected_segmented_percents = [
            SegmentedObject(segment_name='4568', segment_count=0),
            SegmentedObject(segment_name='4636', segment_count=50),
            SegmentedObject(segment_name='4624', segment_count=100),
            SegmentedObject(segment_name='4590', segment_count=0),
        ]
    fetch_segmented_objects = mocker.patch(
        'external_offers.services.grafana_metric.'
        'fetch_segmented_objects',
    )
    fetch_segmented_objects.side_effect = [
        future(all_synced_count),
        future(processed_synced_count),
    ]
    result = await get_segmented_objects(metric, segment_type)

    assert result == expected_segmented_percents
    fetch_segmented_objects.assert_has_calls([
        mocker.call(segment_type=segment_type, metric=metric, processed=False),
        mocker.call(segment_type=segment_type, metric=metric, processed=True),
    ])


@pytest.mark.parametrize(
    'synced_count, processed_synced_count, expected_result',
    [
        (300, 80, 26),
        (0, 100, 0),
        (100, 0, 0),
    ]
)
async def test_get_synced_percentage(
    synced_count, processed_synced_count, expected_result
):
    result = await get_synced_percentage(
        synced_count,
        processed_synced_count,
    )
    assert result == expected_result


async def test_transform_list_into_dict():
    objects = [
        SegmentedObject(segment_name='segment1', segment_count=1),
        SegmentedObject(segment_name='segment2', segment_count=2),
        SegmentedObject(segment_name='segment3', segment_count=3),
    ]
    result = await transform_list_into_dict(objects)
    assert result['segment1'] == 1
    assert result['segment2'] == 2
    assert result['segment3'] == 3


async def test_map_region_codes_to_region_names__returns_result():
    segmented_regions = [
        SegmentedObject(segment_name='4568', segment_count=1),
        SegmentedObject(segment_name='4636', segment_count=3),
    ]
    result = await map_region_codes_to_region_names(segmented_regions)
    expected_result = [
        SegmentedObject(segment_name='respublika-dagestan_4568', segment_count=1),
        SegmentedObject(segment_name='yaroslavskaya-oblast_4636', segment_count=3),
    ]
    assert result == expected_result


async def test_map_region_codes_to_region_names__raises_exception(mocker):
    segmented_regions = [
        SegmentedObject(segment_name='4568', segment_count=1),
        SegmentedObject(segment_name='4636', segment_count=3),
    ]
    mocker.patch(
        'external_offers.services.grafana_metric.get_region_name_from_dict',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.services.grafana_metric.get_region_name_from_api',
        return_value=future(None),
    )
    with pytest.raises(NotFoundRegionNameException):
        await map_region_codes_to_region_names(segmented_regions)


async def test_get_region_name_from_api(mocker):
    non_existing_region_code = '1111111111111111111'
    patched_api = mocker.patch(
        'external_offers.services.grafana_metric.v1_locations_get',
        return_value=future(LocationResponse(name='???????????????????? ????????????????')),
    )
    result = await get_region_name(non_existing_region_code)
    assert result == 'respublika-dagestan'
    patched_api.assert_called_once_with(V1LocationsGet(id=int(non_existing_region_code)))


async def test_get_region_name_from_dict(mocker):
    patched_api = mocker.patch(
        'external_offers.services.grafana_metric.v1_locations_get',
        return_value=future(LocationResponse(name='???????????????????? ????????????????')),
    )
    result = await get_region_name('4568')
    assert result == 'respublika-dagestan'
    patched_api.assert_not_called()


async def test_get_region_from_api__api_client_exception(mocker):
    mocker.patch(
        'external_offers.services.grafana_metric.v1_locations_get',
        side_effect=ApiClientException('error'),
    )
    region_name = await get_region_name_from_api('1234')
    assert region_name is None
