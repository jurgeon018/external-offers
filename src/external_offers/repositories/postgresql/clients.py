from datetime import datetime
from typing import AsyncGenerator, List, Optional

import asyncpgsa
import pytz
from cian_core.runtime_settings import runtime_settings
from sqlalchemy import and_, any_, delete, exists, nullslast, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import false, true
from sqlalchemy.sql.functions import coalesce

from external_offers import pg
from external_offers.entities import Client
from external_offers.enums import ClientStatus, OfferStatus
from external_offers.enums.operator_role import OperatorRole
from external_offers.mappers import client_mapper
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import Status as PublicationStatus
from external_offers.repositories.postgresql.tables import clients, offers_for_call
from external_offers.utils.next_call import get_next_call_date_when_draft


_NO_CALLS = 0
_ONE_CALL = 1

_NO_OFFER_CATEGORY = ''
_CLEAR_PRIORITY = -1


async def get_client_in_progress_by_operator(
    *,
    operator_id: int
) -> Optional[Client]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients]
        ).where(
            and_(
                clients.c.operator_user_id == operator_id,
                clients.c.status == ClientStatus.in_progress.value

            )
        ).limit(1)
    )
    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def assign_suitable_client_to_operator(
    *,
    operator_id: int,
    operator_team_id: Optional[int] = None,
    call_id: str,
    operator_roles: List[str],
    is_test: bool = False,
) -> str:

    now = datetime.now(pytz.utc)

    if runtime_settings.ENABLE_TEAM_PRIORITIES and operator_team_id:
        priority_ordering = (
            nullslast(offers_for_call.c.team_priorities[str(operator_team_id)].asc())
        )
        priority_clause = [
            offers_for_call.c.team_priorities[str(operator_team_id)] != str(_CLEAR_PRIORITY)
        ]
        offer_category_clause = []
    else:
        is_commercial_moderator = OperatorRole.commercial_prepublication_moderator.value in operator_roles
        commercial_category_clause = (
            coalesce(offers_for_call.c.category, _NO_OFFER_CATEGORY)
            .in_(runtime_settings.COMMERCIAL_OFFER_TASK_CREATION_CATEGORIES)
        )

        offer_category_clause = [
            commercial_category_clause
            if is_commercial_moderator
            else ~commercial_category_clause
        ]
        priority_ordering = nullslast(offers_for_call.c.priority.asc())
        priority_clause = [
            offers_for_call.c.priority != _CLEAR_PRIORITY
        ]

    first_suitable_offer_client_cte = (
        select(
            [
                clients.c.client_id,
            ]
        ).select_from(
            clients.join(
                offers_for_call,
                offers_for_call.c.client_id == clients.c.client_id
            )
        ).with_for_update(
            skip_locked=True
        ).where(
            or_(
                # новые клиенты
                and_(
                    # Достает клиентов в ожидании
                    clients.c.unactivated.is_(False),
                    offers_for_call.c.publication_status.is_(None),
                    clients.c.operator_user_id.is_(None),
                    offers_for_call.c.status == OfferStatus.waiting.value,
                    clients.c.status == ClientStatus.waiting.value,
                    clients.c.is_test == is_test,
                    *offer_category_clause,
                    *priority_clause,
                ),
                and_(
                    # Достает перезвоны и недозвоны
                    clients.c.unactivated.is_(False),
                    offers_for_call.c.publication_status.is_(None),
                    clients.c.operator_user_id == operator_id,
                    offers_for_call.c.status.in_([
                        OfferStatus.call_later.value,
                        OfferStatus.call_missed.value,
                    ]),
                    clients.c.next_call <= now,
                    clients.c.is_test == is_test,
                    *offer_category_clause,
                    *priority_clause,
                ),
                # добивочные клиенты
                and_(
                    # Достает добивочных клиентов с неактивироваными черновиками
                    clients.c.unactivated.is_(True),
                    clients.c.operator_user_id == operator_id,
                    clients.c.next_call <= now,
                    offers_for_call.c.publication_status == PublicationStatus.draft.value,
                    clients.c.status.notin_([
                        ClientStatus.declined.value,
                    ]),
                    clients.c.is_test == is_test,
                    *offer_category_clause,
                    *priority_clause,
                ),
                and_(
                    # Достает перезвоны и недозвоны добивочных клиентов с неактивироваными черновиками
                    clients.c.unactivated.is_(True),
                    clients.c.operator_user_id == operator_id,
                    offers_for_call.c.status.in_([
                        OfferStatus.call_later.value,
                        OfferStatus.call_missed.value,
                    ]),
                    clients.c.next_call <= now,
                    offers_for_call.c.publication_status == PublicationStatus.draft.value,
                    clients.c.is_test == is_test,
                    *offer_category_clause,
                    *priority_clause,
                ),
            )
        ).order_by(
            priority_ordering,
            offers_for_call.c.created_at.desc()
        ).limit(
            1
        ).cte(
            'first_suitable_offer_client_cte'
        )
    )
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            operator_user_id=operator_id,
            status=ClientStatus.in_progress.value,
            calls_count=coalesce(clients.c.calls_count, _NO_CALLS) + _ONE_CALL,
            last_call_id=call_id,
            team_id=operator_team_id,
        ).where(
            clients.c.client_id == first_suitable_offer_client_cte.c.client_id
        ).returning(
            clients.c.client_id
        )
    )
    result = await pg.get().fetchval(query, *params)
    return result


async def get_client_unactivated_by_client_id(*, client_id) -> bool:
    query, params = asyncpgsa.compile_query(
        select(
            [clients.c.unactivated]
        ).where(
            clients.c.client_id == client_id
        ).limit(1)
    )
    return await pg.get().fetchval(query, *params)


async def assign_client_to_operator_and_increase_calls_count(
    *,
    client_id: str,
    operator_id: int,
    call_id: str,
) -> Optional[Client]:
    sql = (
        update(
            clients
        ).values(
            operator_user_id=operator_id,
            status=ClientStatus.in_progress.value,
            calls_count=coalesce(clients.c.calls_count, _NO_CALLS) + _ONE_CALL,
            last_call_id=call_id
        ).where(
            clients.c.client_id == client_id
        ).returning(
            clients
        )
    )
    query, params = asyncpgsa.compile_query(sql)
    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def set_client_to_status_and_return(
    *,
    client_id: str,
    status: ClientStatus
) -> Optional[Client]:
    sql = (
        update(
            clients
        ).values(
            status=status.value,
        ).where(
            clients.c.client_id == client_id
        ).returning(
            clients
        )
    )
    query, params = asyncpgsa.compile_query(sql)
    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def set_client_to_status_and_set_next_call_date_and_return(
    *,
    client_id: str,
    next_call: datetime,
    status: ClientStatus
) -> Optional[Client]:
    sql = (
        update(
            clients
        ).values(
            status=status.value,
            next_call=next_call
        ).where(
            clients.c.client_id == client_id,
        ).returning(
            clients
        )
    )
    query, params = asyncpgsa.compile_query(sql)
    row = await pg.get().fetchrow(query, *params)
    res = client_mapper.map_from(row) if row else None
    return res


async def set_client_to_decline_status_and_return(
    *,
    client_id: str
) -> Optional[Client]:
    return await set_client_to_status_and_return(
        client_id=client_id,
        status=ClientStatus.declined
    )


async def set_client_to_call_interrupted_status_and_return(
    *,
    client_id: str
) -> Optional[Client]:
    return await set_client_to_status_and_return(
        client_id=client_id,
        status=ClientStatus.call_interrupted
    )


async def set_client_to_phone_unavailable_status_and_return(
    *,
    client_id: str
) -> Optional[Client]:
    return await set_client_to_status_and_return(
        client_id=client_id,
        status=ClientStatus.phone_unavailable
    )


async def set_client_to_promo_given_status_and_return(
    *,
    client_id: str
) -> Optional[Client]:
    return await set_client_to_status_and_return(
        client_id=client_id,
        status=ClientStatus.promo_given
    )


async def set_client_to_waiting_status_and_return(
    *,
    client_id: str
) -> Optional[Client]:
    return await set_client_to_status_and_return(
        client_id=client_id,
        status=ClientStatus.waiting
    )


async def set_client_to_call_missed_status_set_next_call_and_return(
    *,
    client_id: str,
    next_call: datetime
) -> Optional[Client]:
    return await set_client_to_status_and_set_next_call_date_and_return(
        client_id=client_id,
        status=ClientStatus.call_missed,
        next_call=next_call
    )


async def set_client_to_call_later_status_set_next_call_and_return(
    *,
    client_id: str,
    next_call: datetime
) -> Optional[Client]:
    return await set_client_to_status_and_set_next_call_date_and_return(
        client_id=client_id,
        status=ClientStatus.call_later,
        next_call=next_call
    )


async def save_client(
    *,
    client: Client
) -> None:
    insert_query = insert(clients)

    values = client_mapper.map_to(client)

    query, params = asyncpgsa.compile_query(
        insert_query.values(
            [values]
        )
    )

    await pg.get().execute(query, *params)


async def get_client_by_avito_user_id(
    *,
    avito_user_id: str
) -> Optional[Client]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients]
        ).where(
            clients.c.avito_user_id == avito_user_id,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def get_client_by_client_id(
    *,
    client_id: str
) -> Optional[Client]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients]
        ).where(
            clients.c.client_id == client_id,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def get_client_for_update_by_phone_number(
    *,
    phone_number: str
) -> Optional[Client]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients],
        ).with_for_update(
            skip_locked=True
        ).where(
            any_(clients.c.client_phones) == phone_number,
        ).limit(1)
    )

    row = await pg.get().fetchrow(query, *params)

    return client_mapper.map_from(row) if row else None


async def get_cian_user_id_by_client_id(
    *,
    client_id: str
) -> Optional[int]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients.c.cian_user_id]
        ).where(
            clients.c.client_id == client_id,
        ).limit(1)
    )

    return await pg.get().fetchval(query, *params)


async def get_segment_by_client_id(
    *,
    client_id: str
) -> Optional[str]:
    query, params = asyncpgsa.compile_query(
        select(
            [clients.c.segment]
        ).where(
            clients.c.client_id == client_id,
        ).limit(1)
    )

    return await pg.get().fetchval(query, *params)


async def set_main_cian_user_id_by_client_id(
    *,
    cian_user_id: int,
    client_id: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            cian_user_id=cian_user_id,
            main_account_chosen=True
        ).where(
            clients.c.client_id == client_id,
        )
    )

    await pg.get().execute(query, *params)


async def set_cian_user_id_by_client_id(
    *,
    cian_user_id: int,
    client_id: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            cian_user_id=cian_user_id,
        ).where(
            clients.c.client_id == client_id,
        )
    )

    await pg.get().execute(query, *params)


async def set_phone_number_by_client_id(
    *,
    client_id: str,
    phone_number: str
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            client_phones=[phone_number]
        ).where(
            clients.c.client_id == client_id,
        )
    )

    await pg.get().execute(query, *params)


async def set_comment_by_client_id(
    *,
    client_id: str,
    comment: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            comment=comment
        ).where(
            clients.c.client_id == client_id,
        )
    )
    await pg.get().execute(query, *params)


async def set_reason_of_decline_by_client_id(
        *,
        client_id: str,
        reason_of_decline: Optional[str] = None,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            reason_of_decline=reason_of_decline
        ).where(
            clients.c.client_id == client_id,
            )
    )
    await pg.get().execute(query, *params)


async def set_additional_numbers_by_client_id(
        *,
        client_id: str,
        additional_numbers: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            additional_numbers=additional_numbers
        ).where(
            clients.c.client_id == client_id,
            )
    )
    await pg.get().execute(query, *params)


async def set_additional_emails_by_client_id(
        *,
        client_id: str,
        additional_emails: str,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            additional_emails=additional_emails
        ).where(
            clients.c.client_id == client_id,
            )
    )
    await pg.get().execute(query, *params)


async def set_client_accepted_and_no_operator_if_no_offers_in_progress(
    *,
    client_id: str
) -> bool:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            status=ClientStatus.accepted.value,
        ).where(
            and_(
                clients.c.client_id == client_id,
                ~exists(
                    select(
                        [1]
                    ).where(
                        and_(
                            offers_for_call.c.client_id == client_id,
                            offers_for_call.c.status == OfferStatus.in_progress.value
                        )
                    )
                )
            )
        ).returning(
            clients.c.client_id
        )
    )

    client_id = await pg.get().fetchval(query, *params)

    return bool(client_id)


async def update_clients_operator(
    *,
    old_operator_id: int,
    new_operator_id: int,
) -> None:
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            operator_user_id=new_operator_id,
        ).where(
            clients.c.operator_user_id == old_operator_id,
        )
    )
    await pg.get().execute(query, *params)


async def get_client_id_by_offer_cian_id(offer_cian_id: int) -> str:
    query, params = asyncpgsa.compile_query(
        select(
            [offers_for_call.c.client_id]
        ).where(
            offers_for_call.c.offer_cian_id == offer_cian_id,
        ).limit(1)
    )
    client_id = await pg.get().fetchval(query, *params)
    return client_id


async def set_client_done_by_offer_cian_id(
        *,
        offer_cian_id: int,
        published_at: datetime,
) -> None:
    client_id = await get_client_id_by_offer_cian_id(
        offer_cian_id=offer_cian_id,
    )
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            unactivated=False,
            published_at=published_at,
            next_call=None,
            status=ClientStatus.accepted.value,
        ).where(
            clients.c.client_id == client_id
        )
    )
    await pg.get().execute(query, *params)


async def set_client_unactivated_by_offer_cian_id(
        *,
        offer_cian_id: int,
        drafted_at: datetime,
) -> None:
    """
    Помечает добивочных клиентов, обнуляет номер попытки звонка,
    и проставляет новую дату для следующего прозвона(+3 дня)
    """
    client_id = await get_client_id_by_offer_cian_id(offer_cian_id)
    query, params = asyncpgsa.compile_query(
        update(
            clients
        ).values(
            drafted_at=drafted_at,
            unactivated=True,
            calls_count=0,
            next_call=get_next_call_date_when_draft(),
        ).where(
            clients.c.client_id == client_id
        )
    )
    await pg.get().execute(query, *params)


async def delete_test_clients() -> None:
    query, params = asyncpgsa.compile_query(
        delete(
            clients
        ).where(
            clients.c.is_test == true()
        )
    )
    await pg.get().execute(query, *params)


async def iterate_over_clients_sorted(
    *,
    prefetch: int
) -> AsyncGenerator[Client, None]:

    query, params = asyncpgsa.compile_query(
        select(
            [clients]
        ).where(
            clients.c.is_test == false()
        ).order_by(
            clients.c.client_id.asc()
        )
    )
    cursor = await pg.get().cursor(
        query,
        *params,
        prefetch=prefetch
    )
    async for row in cursor:
        yield client_mapper.map_from(row)
