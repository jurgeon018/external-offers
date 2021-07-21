from typing import List
from external_offers.entities.grafana_metric import SegmentedObject
from external_offers.enums.grafana_metric import GrafanaMetric, GrafanaSegmentType
from external_offers import pg


# grafana

async def get_clients_with_more_than_1_offer_query():
    return """
            SELECT client_id
            FROM offers_for_call as ofc
            GROUP BY ofc.client_id
            HAVING COUNT(1) > 1
    """


async def get_unsynced_waiting_objects_count(table_name: str) -> str:
    """ получить количество заданий в ожидании, у клиентов которых больше 1 задания"""
    clients_with_more_than_1_offer_query = await get_clients_with_more_than_1_offer_query()
    row = await pg.get().fetchrow(f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE synced_with_grafana IS NOT TRUE
        AND status = 'waiting'
        AND client_id IN ({clients_with_more_than_1_offer_query});
    """)
    return row['count']


async def sync_waiting_objects_with_grafana(table_name: str) -> None:
    clients_with_more_than_1_offer_query = await get_clients_with_more_than_1_offer_query() 
    await pg.get().execute(f"""
        UPDATE {table_name}
        SET synced_with_grafana = TRUE
        WHERE synced_with_grafana IS NOT TRUE
        AND status = 'waiting'
        AND client_id IN ({clients_with_more_than_1_offer_query});
    """)


async def get_processed_synced_objects_count(table_name: str) -> str:
    row = await pg.get().fetchrow(f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE synced_with_grafana IS TRUE
        AND status <> 'waiting';
    """)
    return row['count']


async def get_synced_objects_count(table_name: str) -> str:
    row = await pg.get().fetchrow(f"""
        SELECT COUNT(*) FROM {table_name}
        WHERE synced_with_grafana IS TRUE;
    """)
    return row['count']


async def unsync_objects_with_grafana(table_name: str) -> None:
    await pg.get().execute(f"""
        UPDATE {table_name}
        SET synced_with_grafana = NULL
        WHERE synced_with_grafana IS TRUE;
    """)


async def fetch_segmented_objects(
    segment_type: GrafanaSegmentType,
    metric: GrafanaMetric,
    processed: bool = None,
) -> List[SegmentedObject]:
    offer_metrics = [
        GrafanaMetric.waiting_offers_count,
        GrafanaMetric.processed_offers_count,
        GrafanaMetric.processed_offers_percentage,
    ]
    client_metrics = [
        GrafanaMetric.waiting_clients_count,
        GrafanaMetric.processed_clients_count,
        GrafanaMetric.processed_clients_percentage,
    ]
    segment_types_to_field_names_mapper = {
        GrafanaSegmentType.region: "parsed_offers.source_object_model->>'region'",
        GrafanaSegmentType.user_segment: 'parsed_offers.user_segment',
        GrafanaSegmentType.category: 'ofc.category',
    }
    field_name = segment_types_to_field_names_mapper[segment_type]
    clients_with_more_than_1_offer_query = await get_clients_with_more_than_1_offer_query()
    if metric == GrafanaMetric.waiting_offers_count:
        status_query = f"""
        WHERE ofc.synced_with_grafana IS NOT TRUE
        AND ofc.status = 'waiting'
        AND ofc.client_id IN ({clients_with_more_than_1_offer_query})
        """
    elif metric == GrafanaMetric.waiting_clients_count:
        status_query = f"""
        WHERE clients.synced_with_grafana IS NOT TRUE
        AND clients.status = 'waiting'
        AND clients.client_id IN ({clients_with_more_than_1_offer_query})
        """
    elif metric == GrafanaMetric.processed_offers_count:
        status_query = f"""
        WHERE ofc.synced_with_grafana IS TRUE
        AND ofc.status <> 'waiting'
        """
    elif metric == GrafanaMetric.processed_clients_count:
        status_query = f"""
        WHERE clients.synced_with_grafana IS TRUE
        AND clients.status <> 'waiting'
        """
    elif metric == GrafanaMetric.processed_offers_percentage:
        if processed is True:
            status_query = """
            WHERE ofc.synced_with_grafana IS TRUE
            AND clients.status <> 'waiting' 
            """
        elif processed is False:
            status_query = """
            WHERE ofc.synced_with_grafana IS TRUE
            """
    elif metric == GrafanaMetric.processed_clients_percentage:
        if processed is True:
            status_query = """
            WHERE clients.synced_with_grafana IS TRUE
            AND clients.status <> 'waiting'
            """
        elif processed is False:
            status_query = """
            WHERE clients.synced_with_grafana IS TRUE
            """

    if metric in client_metrics:
        segmentation_query = f"""
            SELECT {field_name} AS segment_name, ofc.client_id as client_id
            FROM offers_for_call as ofc
            JOIN clients
                ON clients.client_id = ofc.client_id
            JOIN parsed_offers
                ON parsed_offers.id = ofc.parsed_id
            {status_query};
        """
        rows = await pg.get().fetch(segmentation_query)

        # создает словарь со списками клиентов из сегментов
        dct = {}
        for row in rows: 
            segment_name = row['segment_name']
            client_id = row['client_id']
            try:
                if client_id not in dct[segment_name]: 
                    dct[segment_name].append(client_id)
            except KeyError:
                dct[segment_name] = [client_id,]

        # получает количество уникальных клиентов через len
        rows = [
            {
                'segment_name': segment_name,
                "segment_count": len(client_ids)
            } for segment_name, client_ids in dct.items()
        ]

    elif metric in offer_metrics:
        segmentation_query = f"""
            SELECT {field_name} AS segment_name, COUNT({field_name}) AS segment_count
            FROM offers_for_call as ofc
            JOIN clients
                ON clients.client_id = ofc.client_id
            JOIN parsed_offers
                ON parsed_offers.id = ofc.parsed_id
            {status_query}
            GROUP BY {field_name};
        """
        rows = await pg.get().fetch(segmentation_query)

    return [
        SegmentedObject(
            segment_name=row['segment_name'],
            segment_count=row['segment_count'],
        ) for row in rows
    ] 
