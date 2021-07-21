from datetime import datetime, timedelta
from typing import AsyncGenerator, List, Optional

import asyncpgsa
import pytz
from cian_core.runtime_settings import runtime_settings
from simple_settings import settings
from sqlalchemy import and_, delete, func, not_, or_, outerjoin, over, select, update
from sqlalchemy.dialects.postgresql import insert

from external_offers import pg
from external_offers.entities import ClientWaitingOffersCount, EnrichedOffer, Offer
from external_offers.entities.grafana_metric import SegmentedObject
from external_offers.entities.offers import OfferForPrioritization
from external_offers.enums import OfferStatus
from external_offers.enums.grafana_metric import GrafanaMetric, GrafanaSegmentType
from external_offers.mappers import (
    client_waiting_offers_count_mapper,
    enriched_offer_mapper,
    offer_for_prioritization_mapper,
    offer_mapper,
)
from external_offers.repositories.postgresql.tables import clients, offers_for_call, parsed_offers
from external_offers.services.prioritizers.build_priority import build_call_later_priority, build_call_missed_priority
from external_offers.utils import iterate_over_list_by_chunks


_REGION_FIELD = 'region'


waiting_offers_counts_cte = (
    select(
        [
            offers_for_call.c.id,
            offers_for_call.c.client_id,
            over(func.count(), partition_by=offers_for_call.c.client_id).label('waiting_offers_count')
        ]
    )
    .where(
        offers_for_call.c.status == OfferStatus.waiting.value,
    )
    .cte('waiting_offers_counts_cte')
)


async def save_offer_for_call(*, offer: Offer) -> None:
    insert_query = insert(offers_for_call)

    values = offer_mapper.map_to(offer)

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        )
    )

    await pg.get().execute(query, *params)


async def get_offers_in_progress_by_operator(*, operator_id: int) -> list[Offer]:
    query = """
        SELECT
            ofc.*
        FROM
            offers_for_call as ofc
        INNER JOIN
            clients as c
        ON
            ofc.client_id = c.client_id
        WHERE
            ofc.status = 'inProgress'
            AND c.operator_user_id = $1
    """

    rows = await pg.get().fetch(query, operator_id)

    return [offer_mapper.map_from(row) for row in rows]


async def get_enriched_offers_in_progress_by_operator(*, operator_id: int) -> list[EnrichedOffer]:
    query = """
        SELECT
            ofc.*,
            po.source_object_model->>'title' as title,
            po.source_object_model->>'address' as address
        FROM
            offers_for_call as ofc
        INNER JOIN
            clients as c
        ON
            ofc.client_id = c.client_id
        INNER JOIN
            parsed_offers as po
        ON
            ofc.parsed_id = po.id
        WHERE
            ofc.status = 'inProgress'
            AND c.operator_user_id = $1
    """

    rows = await pg.get().fetch(query, operator_id)

    return [enriched_offer_mapper.map_from(row) for row in rows]


async def exists_offers_in_progress_by_operator(*, operator_id: int) -> bool:
    query = """
        SELECT
            1
        FROM
            offers_for_call as ofc
        INNER JOIN
            clients as c
        ON
            ofc.client_id = c.client_id
        WHERE
            ofc.status = 'inProgress'
            AND c.operator_user_id = $1
        LIMIT 1
    """

    exists = await pg.get().fetchval(query, operator_id)

    return exists


async def exists_offers_in_progress_by_operator_and_offer_id(*, operator_id: int, offer_id: str) -> bool:
    query, params = asyncpgsa.compile_query(
        select(
            [1]
        ).select_from(
            offers_for_call.join(
                clients,
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).where(
            and_(
                offers_for_call.c.status == OfferStatus.in_progress.value,
                clients.c.operator_user_id == operator_id,
                offers_for_call.c.id == offer_id
            )
        ).limit(1)
    )

    exists = await pg.get().fetchval(query, *params)

    return bool(exists)


async def exists_offers_in_progress_by_client(*, client_id: str) -> bool:
    query, params = asyncpgsa.compile_query(
        select(
            [1]
        ).select_from(
            offers_for_call.join(
                clients,
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).where(
            and_(
                offers_for_call.c.status == OfferStatus.in_progress.value,
                clients.c.client_id == client_id,
            )
        ).limit(1)
    )

    exists = await pg.get().fetchval(query, *params)

    return bool(exists)


async def exists_offers_draft_by_client(*, client_id: str) -> bool:
    query, params = asyncpgsa.compile_query(
        select(
            [1]
        ).select_from(
            offers_for_call.join(
                clients,
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).where(
            and_(
                offers_for_call.c.status == OfferStatus.draft.value,
                clients.c.client_id == client_id,
            )
        ).limit(1)
    )

    exists = await pg.get().fetchval(query, *params)

    return bool(exists)


async def set_undrafted_offers_in_progress_by_client(
    *,
    client_id: str,
    call_id: str,
) -> list[str]:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.in_progress.value,
            last_call_id=call_id
        ).where(
            and_(
                offers_for_call.c.client_id == client_id,
                offers_for_call.c.status != OfferStatus.draft.value
            )
        ).returning(
            offers_for_call.c.id
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    result = await pg.get().fetch(query, *params)
    return [r['id'] for r in result]


async def set_offers_declined_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.declined
    )


async def set_offers_call_interrupted_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.call_interrupted
    )


async def set_offers_phone_unavailable_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.phone_unavailable
    )


async def set_offers_promo_given_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.promo_given
    )


async def set_offers_call_missed_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.call_missed,
        priority=build_call_missed_priority()
    )


async def set_offers_call_later_by_client(*, client_id: str) -> list[str]:
    return await set_offers_status_and_priority_by_client(
        client_id=client_id,
        status=OfferStatus.call_later,
        priority=build_call_later_priority()
    )


async def set_offers_status_and_priority_by_client(
    *,
    client_id: str,
    status: OfferStatus,
    priority: Optional[int] = None
) -> list[str]:
    values = {
        'status': status.value
    }

    if priority:
        values['priority'] = priority

    sql = (
        update(
            offers_for_call
        ).values(
            **values
        ).where(
            and_(
                offers_for_call.c.client_id == client_id,
                offers_for_call.c.status == OfferStatus.in_progress.value
            )
        ).returning(
            offers_for_call.c.id
        )
    )

    query, params = asyncpgsa.compile_query(sql)
    result = await pg.get().fetch(query, *params)

    return [r['id'] for r in result]


async def set_offer_draft_by_offer_id(*, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.draft.value,
        ).where(
            and_(
                offers_for_call.c.id == offer_id,
                offers_for_call.c.status == OfferStatus.in_progress.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def set_offer_cancelled_by_offer_id(*, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.cancelled.value,
        ).where(
            and_(
                offers_for_call.c.id == offer_id,
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def set_offer_already_published_by_offer_id(*, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            status=OfferStatus.already_published.value,
        ).where(
            and_(
                offers_for_call.c.id == offer_id,
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def get_offer_by_parsed_id(*, parsed_id: str) -> Optional[Offer]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call]
        ).where(
            offers_for_call.c.parsed_id == parsed_id,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return offer_mapper.map_from(row) if row else None


async def get_offer_by_offer_id(*, offer_id: str) -> Optional[Offer]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call]
        ).where(
            offers_for_call.c.id == offer_id,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return offer_mapper.map_from(row) if row else None


async def get_offers_parsed_ids_by_parsed_ids(*, parsed_ids: list[str]) -> Optional[list[str]]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.parsed_id]
        ).where(
            offers_for_call.c.parsed_id.in_(parsed_ids),
        )
    )

    rows = await pg.get().fetch(query, *params)

    return rows


async def set_waiting_offers_priority_by_offer_ids(*, offer_ids: list[str], priority: int) -> None:
    for offer_ids_chunk in iterate_over_list_by_chunks(
        iterable=offer_ids,
        chunk_size=runtime_settings.SET_WAITING_OFFERS_PRIORITY_BY_OFFER_IDS_CHUNK
    ):
        sql = (
            update(
                offers_for_call
            ).values(
                priority=priority
            ).where(
                and_(
                    offers_for_call.c.status == OfferStatus.waiting.value,
                    offers_for_call.c.id.in_(offer_ids_chunk),
                )
            )
        )

        query, params = asyncpgsa.compile_query(sql)
        await pg.get().execute(query, *params)


async def get_last_sync_date() -> Optional[datetime]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.synced_at]
        ).order_by(
            offers_for_call.c.synced_at.desc()
        ).limit(1)
    )
    return await pg.get().fetchval(query, *params)


async def get_offer_cian_id_by_offer_id(*, offer_id: str) -> Optional[int]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.offer_cian_id]
        ).where(
            offers_for_call.c.id == offer_id
        )
    )

    return await pg.get().fetchval(query, *params)


async def set_offer_cian_id_by_offer_id(*, offer_cian_id: int, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            offer_cian_id=offer_cian_id,
        ).where(
            offers_for_call.c.id == offer_id,
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def get_offer_promocode_by_offer_id(*, offer_id: str) -> Optional[str]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.promocode]
        ).where(
            offers_for_call.c.id == offer_id
        )
    )

    return await pg.get().fetchval(query, *params)


async def set_offer_promocode_by_offer_id(*, promocode: str, offer_id: str) -> None:
    sql = (
        update(
            offers_for_call
        ).values(
            promocode=promocode,
        ).where(
            offers_for_call.c.id == offer_id,
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def try_to_lock_offer_and_return_status(*, offer_id: str) -> Optional[str]:
    query = """
        SELECT
            status
        FROM
            offers_for_call as ofc
        WHERE
            ofc.id = $1
        FOR UPDATE SKIP LOCKED
    """

    status = await pg.get().fetchval(query, offer_id)

    return status


async def delete_waiting_offers_for_call_by_client_ids(*, client_ids: list[str]) -> None:
    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.status == OfferStatus.waiting.value,
                offers_for_call.c.client_id.in_(client_ids)
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_waiting_offers_for_call_by_parsed_ids(*, parsed_ids: list[str]) -> None:
    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.parsed_id.in_(parsed_ids),
                offers_for_call.c.status == OfferStatus.waiting.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_waiting_offers_for_call_without_parsed_offers() -> None:
    offers_and_parsed_offers = outerjoin(
            left=offers_for_call,
            right=parsed_offers,
            onclause=offers_for_call.c.parsed_id == parsed_offers.c.id
    )

    waiting_offers_without_parsed_cte = (
        select(
            [
                offers_for_call.c.id,
            ]
        )
        .select_from(
            offers_and_parsed_offers
        )
        .where(
            and_(
                offers_for_call.c.status == OfferStatus.waiting.value,
                parsed_offers.c.id.is_(None)
            )
        )
        .cte('waiting_offers_without_parsed_cte')
    )

    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.id == waiting_offers_without_parsed_cte.c.id,
                offers_for_call.c.status == OfferStatus.waiting.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_waiting_offers_for_call_with_count_off_limit() -> None:
    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.id == waiting_offers_counts_cte.c.id,
                or_(
                    settings.OFFER_TASK_CREATION_MINIMUM_OFFERS > waiting_offers_counts_cte.c.waiting_offers_count,
                    settings.OFFER_TASK_CREATION_MAXIMUM_OFFERS < waiting_offers_counts_cte.c.waiting_offers_count
                )
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_old_waiting_offers_for_call() -> None:
    max_waiting_offer_age_in_days = runtime_settings.get(
        'CLEAR_WAITING_OFFERS_FOR_CALL_AGE_IN_DAYS',
        settings.CLEAR_WAITING_OFFERS_FOR_CALL_AGE_IN_DAYS
    )
    clear_border = (
        datetime.now(pytz.utc)
        - timedelta(days=max_waiting_offer_age_in_days)
    )

    sql = (
        delete(
            offers_for_call
        ).where(
            and_(
                offers_for_call.c.parsed_created_at <= clear_border,
                offers_for_call.c.status == OfferStatus.waiting.value
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def delete_waiting_clients_with_count_off_limit() -> None:
    sql = (
        delete(
            clients
        ).where(
            and_(
                clients.c.client_id == waiting_offers_counts_cte.c.client_id,
                or_(
                    settings.OFFER_TASK_CREATION_MINIMUM_OFFERS > waiting_offers_counts_cte.c.waiting_offers_count,
                    settings.OFFER_TASK_CREATION_MAXIMUM_OFFERS < waiting_offers_counts_cte.c.waiting_offers_count
                )
            )
        )
    )

    query, params = asyncpgsa.compile_query(sql)

    await pg.get().execute(query, *params)


async def get_waiting_offer_counts_by_clients() -> list[ClientWaitingOffersCount]:
    sql = (
        select(
            [waiting_offers_counts_cte]
        ).distinct(
            waiting_offers_counts_cte.c.client_id
        )
    )

    query, params = asyncpgsa.compile_query(sql)
    rows = await pg.get().fetch(query, *params)
    return [client_waiting_offers_count_mapper.map_from(row) for row in rows]


async def get_waiting_offers_for_call() -> AsyncGenerator[OfferForPrioritization, None]:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call]
        ).where(
            offers_for_call.c.status == OfferStatus.waiting.value,
        )
    )
    cursor = await pg.get().cursor(
        query,
        *params,
        prefetch=runtime_settings.WAITING_OFFERS_FOR_CALL_PREFETCH,
    )
    async for row in cursor:
        yield offer_for_prioritization_mapper.map_from(row)


async def get_offers_regions_by_client_id(*, client_id: str) -> list[int]:
    query, params = asyncpgsa.compile_query(
        select(
            [
                parsed_offers.c.source_object_model[_REGION_FIELD].as_integer().label(_REGION_FIELD)
            ]
        ).select_from(
            clients.join(
                offers_for_call.join(
                    parsed_offers,
                    offers_for_call.c.parsed_id == parsed_offers.c.id
                ),
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).where(
            and_(
                clients.c.client_id == client_id,
                offers_for_call.c.status == OfferStatus.waiting.value,
            )
        )
    )

    rows = await pg.get().fetch(query, *params)

    return [row[_REGION_FIELD] for row in rows]


async def iterate_over_offers_for_call_sorted(
    *,
    prefetch=settings.DEFAULT_PREFETCH,
) -> AsyncGenerator[Offer, None]:
    non_final_statuses = [
        OfferStatus.waiting.value,
        OfferStatus.in_progress.value,
        OfferStatus.call_missed.value,
        OfferStatus.call_later.value,
    ]
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call]
        ).where(
            or_(
                # все обьявления в нефинальных статусах отправляются в кафку повторно
                offers_for_call.c.status.in_(non_final_statuses),
                # все обьявления с финальным статусом отправляются в кафку единажды
                # (отправляются только те, которые еще не были отправлены в кафку)
                and_(
                    offers_for_call.c.status.notin_(non_final_statuses),
                    not_(offers_for_call.c.synced_with_kafka),
                ),
            )
        ).order_by(
            offers_for_call.c.created_at.asc(),
            offers_for_call.c.id.asc()
        )
    )
    cursor = await pg.get().cursor(
        query,
        *params,
        prefetch=prefetch
    )
    async for row in cursor:
        yield offer_mapper.map_from(row)


async def sync_offers_for_call_with_kafka_by_ids(offer_ids: list[int]) -> None:
    non_final_statuses = [
        OfferStatus.waiting.value,
        OfferStatus.in_progress.value,
        OfferStatus.call_missed.value,
        OfferStatus.call_later.value,
    ]
    for offer_ids_chunk in iterate_over_list_by_chunks(
        iterable=offer_ids,
        chunk_size=runtime_settings.SYNC_OFFERS_FOR_CALL_WITH_KAFKA_BY_IDS_CHUNK
    ):
        sql = (
            update(
                offers_for_call
            ).values(
                synced_with_kafka=True
            ).where(
                and_(
                    offers_for_call.c.id.in_(offer_ids_chunk),
                    # проставляет флаг только заданиям в финальных статусах
                    offers_for_call.c.status.notin_(non_final_statuses),
                )
            )
        )
        query, params = asyncpgsa.compile_query(sql)
        await pg.get().fetch(query, *params)


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
