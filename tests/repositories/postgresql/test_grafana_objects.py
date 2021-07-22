import pytest
from cian_test_utils import future

from external_offers import pg
from external_offers.entities.grafana_metric import SegmentedObject
from external_offers.enums.grafana_metric import GrafanaMetric, GrafanaSegmentType
from external_offers.repositories.postgresql.grafana_objects import (
    fetch_segmented_objects,
    get_clients_with_more_than_1_offer_query,
    get_processed_synced_objects_count,
    get_synced_objects_count,
    get_unsynced_waiting_objects_count,
    metric_to_status_query_mapper,
    segment_types_to_field_names_mapper,
    sync_waiting_objects_with_grafana,
    unsync_objects_with_grafana,
)


async def test_get_clients_with_more_than_1_offer_query():
    # arrange
    expected_result = """
            SELECT client_id
            FROM offers_for_call as ofc
            GROUP BY ofc.client_id
            HAVING COUNT(1) > 1
    """
    # act
    result = get_clients_with_more_than_1_offer_query()
    # assert
    assert result == expected_result


async def test_get_unsynced_waiting_objects_count(mocker):
    # arrange
    return_value = 1
    table_name = 'offers_for_call'
    pg.get().fetchval.return_value = future(return_value)
    expected_query = f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE synced_with_grafana IS NOT TRUE
        AND status = 'waiting'
        AND client_id IN (
            SELECT client_id
            FROM offers_for_call as ofc
            GROUP BY ofc.client_id
            HAVING COUNT(1) > 1
    );
    """
    # act
    result = await get_unsynced_waiting_objects_count(table_name)
    # assert
    pg.get().fetchval.assert_called_once_with(expected_query)
    assert result == return_value


async def test_sync_waiting_objects_with_grafana(mocker):
    # arrange
    return_value = None
    table_name = 'offers_for_call'
    pg.get().fetchval.return_value = future(return_value)
    expected_query = f"""
        UPDATE {table_name}
        SET synced_with_grafana = TRUE
        WHERE synced_with_grafana IS NOT TRUE
        AND status = 'waiting'
        AND client_id IN (
            SELECT client_id
            FROM offers_for_call as ofc
            GROUP BY ofc.client_id
            HAVING COUNT(1) > 1
    );
    """
    # act
    result = await sync_waiting_objects_with_grafana(table_name)
    # assert
    pg.get().execute.assert_called_once_with(expected_query)
    assert result == return_value


async def test_get_processed_synced_objects_count(mocker):
    # arrange
    return_value = 1
    table_name = 'offers_for_call'
    pg.get().fetchval.return_value = future(return_value)
    expected_query = f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE synced_with_grafana IS TRUE
        AND status <> 'waiting';
    """
    # act
    result = await get_processed_synced_objects_count(table_name)
    # assert
    pg.get().fetchval.assert_called_once_with(expected_query)
    assert result == return_value


async def test_get_synced_objects_count(mocker):
    # arrange
    return_value = 1
    table_name = 'offers_for_call'
    pg.get().fetchval.return_value = future(return_value)
    expected_query = f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE synced_with_grafana IS TRUE;
    """
    # act
    result = await get_synced_objects_count(table_name)
    # assert
    pg.get().fetchval.assert_called_once_with(expected_query)
    assert result == return_value


async def test_unsync_objects_with_grafana(mocker):
    # arrange
    return_value = None
    table_name = 'offers_for_call'
    pg.get().fetchval.return_value = future(return_value)
    expected_query = f"""
        UPDATE {table_name}
        SET synced_with_grafana = NULL
        WHERE synced_with_grafana IS TRUE;
    """
    # act
    result = await unsync_objects_with_grafana(table_name)
    # assert
    pg.get().execute.assert_called_once_with(expected_query)
    assert result == return_value


client_query = """
    SELECT {{field_name}} AS segment_name, ofc.client_id as client_id
    FROM offers_for_call as ofc
    JOIN clients
        ON clients.client_id = ofc.client_id
    JOIN parsed_offers
        ON parsed_offers.id = ofc.parsed_id
    {{status_query}};
"""
client_return_value = [
    {"client_id": 1, "segment_name": "name1"},
    {"client_id": 2, "segment_name": "name2"},
    {"client_id": 3, "segment_name": "name4"},
    {"client_id": 4, "segment_name": "name4"},
    {"client_id": 5, "segment_name": "name1"},
    {"client_id": 6, "segment_name": "name1"},
    {"client_id": 7, "segment_name": "name3"},
    {"client_id": 8, "segment_name": "name4"},
    {"client_id": 9, "segment_name": "name4"},
]
client_expected_result = [
    SegmentedObject(segment_name="name1", segment_count=3),
    SegmentedObject(segment_name="name2", segment_count=1),
    SegmentedObject(segment_name="name4", segment_count=4),
    SegmentedObject(segment_name="name3", segment_count=1),
]
offer_query = """
    SELECT {{field_name}} AS segment_name, COUNT({{field_name}}) AS segment_count
    FROM offers_for_call as ofc
    JOIN clients
        ON clients.client_id = ofc.client_id
    JOIN parsed_offers
        ON parsed_offers.id = ofc.parsed_id
    {{status_query}}
    GROUP BY {{field_name}};
"""
offer_return_value = [
    {"segment_count": 1, "segment_name": "name1"},
    {"segment_count": 4, "segment_name": "name2"},
    {"segment_count": 2, "segment_name": "name3"},
    {"segment_count": 9, "segment_name": "name4"},
]
offer_expected_result = [
    SegmentedObject(segment_name="name1", segment_count=1),
    SegmentedObject(segment_name="name2", segment_count=4),
    SegmentedObject(segment_name="name3", segment_count=2),
    SegmentedObject(segment_name="name4", segment_count=9),
]
argvalues = [
    # client
    # waiting_clients_count
    (GrafanaMetric.waiting_clients_count, GrafanaSegmentType.category, 
        None, client_query, client_return_value, client_expected_result),
    (GrafanaMetric.waiting_clients_count, GrafanaSegmentType.region, 
        None, client_query, client_return_value, client_expected_result),
    (GrafanaMetric.waiting_clients_count, GrafanaSegmentType.user_segment, 
        None, client_query, client_return_value, client_expected_result),
    # processed_clients_count
    (GrafanaMetric.processed_clients_count, GrafanaSegmentType.category, 
        None, client_query, client_return_value, client_expected_result),
    (GrafanaMetric.processed_clients_count, GrafanaSegmentType.region, 
        None, client_query, client_return_value, client_expected_result),
    (GrafanaMetric.processed_clients_count, GrafanaSegmentType.user_segment, 
        None, client_query, client_return_value, client_expected_result),
    # processed_clients_percentage True
    (GrafanaMetric.processed_clients_percentage, GrafanaSegmentType.category, 
        True, client_query, client_return_value, client_expected_result),
    (GrafanaMetric.processed_clients_percentage, GrafanaSegmentType.region, 
        True, client_query, client_return_value, client_expected_result),
    (GrafanaMetric.processed_clients_percentage, GrafanaSegmentType.user_segment, 
        True, client_query, client_return_value, client_expected_result),
    # processed_clients_percentage False
    (GrafanaMetric.processed_clients_percentage, GrafanaSegmentType.category, 
        False, client_query, client_return_value, client_expected_result),
    (GrafanaMetric.processed_clients_percentage, GrafanaSegmentType.region, 
        False, client_query, client_return_value, client_expected_result),
    (GrafanaMetric.processed_clients_percentage, GrafanaSegmentType.user_segment, 
        False, client_query, client_return_value, client_expected_result),
    # offers
    # waiting_offers_count
    (GrafanaMetric.waiting_offers_count, GrafanaSegmentType.category, 
        None, offer_query, offer_return_value, offer_expected_result),
    (GrafanaMetric.waiting_offers_count, GrafanaSegmentType.region, 
        None, offer_query, offer_return_value, offer_expected_result),
    (GrafanaMetric.waiting_offers_count, GrafanaSegmentType.user_segment, 
        None, offer_query, offer_return_value, offer_expected_result),
    # processed_offers_count
    (GrafanaMetric.processed_offers_count, GrafanaSegmentType.category, 
        None, offer_query, offer_return_value, offer_expected_result),
    (GrafanaMetric.processed_offers_count, GrafanaSegmentType.region, 
        None, offer_query, offer_return_value, offer_expected_result),
    (GrafanaMetric.processed_offers_count, GrafanaSegmentType.user_segment, 
        None, offer_query, offer_return_value, offer_expected_result),
    # processed_offers_percentage True
    (GrafanaMetric.processed_offers_percentage, GrafanaSegmentType.category, 
        True, offer_query, offer_return_value, offer_expected_result),
    (GrafanaMetric.processed_offers_percentage, GrafanaSegmentType.region, 
        True, offer_query, offer_return_value, offer_expected_result),
    (GrafanaMetric.processed_offers_percentage, GrafanaSegmentType.user_segment, 
        True, offer_query, offer_return_value, offer_expected_result),
    # processed_offers_percentage False
    (GrafanaMetric.processed_offers_percentage, GrafanaSegmentType.category, 
        False, offer_query, offer_return_value, offer_expected_result),
    (GrafanaMetric.processed_offers_percentage, GrafanaSegmentType.region, 
        False, offer_query, offer_return_value, offer_expected_result),
    (GrafanaMetric.processed_offers_percentage, GrafanaSegmentType.user_segment, 
        False, offer_query, offer_return_value, offer_expected_result),
]


@pytest.mark.parametrize(
    'metric, segment_type, processed, expected_query, return_value, expected_result',
    argvalues
)
async def test_fetch_segmented_clients_with_count_metrics(
    metric,
    segment_type,
    processed,
    expected_query,
    return_value,
    expected_result,
):
    # arrange
    field_name = segment_types_to_field_names_mapper[segment_type]
    status_query = metric_to_status_query_mapper[metric]
    expected_query = expected_query.format(field_name=field_name, status_query=status_query)
    pg.get().fetch.return_value = future(return_value)
    # act
    result = await fetch_segmented_objects(segment_type, metric, processed)
    # assert
    assert pg.get().fetch.assect_called_once_with(expected_query)
    assert result == expected_result
