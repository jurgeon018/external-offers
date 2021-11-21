import logging
from typing import Callable, Optional

from external_offers import pg
from external_offers.entities.admin import (
    AdminCallInterruptedClientRequest,
    AdminCallLaterClientRequest,
    AdminCallMissedClientRequest,
    AdminDeclineClientRequest,
    AdminDeleteOfferRequest,
    AdminError,
    AdminPhoneUnavailableClientRequest,
    AdminPromoGivenClientRequest,
    AdminResponse,
    AdminUpdateOffersListRequest,
)
from external_offers.entities.clients import Client
from external_offers.entities.offers import Offer
from external_offers.enums import CallStatus, OfferStatus
from external_offers.helpers.uuid import generate_guid
from external_offers.queue.helpers import send_kafka_calls_analytics_message_if_not_test
from external_offers.repositories.postgresql import (
    assign_suitable_client_to_operator,
    exists_offers_draft_by_client,
    exists_offers_in_progress_by_client,
    exists_offers_in_progress_by_operator,
    get_client_by_client_id,
    get_offer_by_offer_id,
    save_event_log_for_offers,
    set_client_accepted_and_no_operator_if_no_offers_in_progress,
    set_client_to_call_interrupted_status_and_return,
    set_client_to_call_later_status_set_next_call_and_return,
    set_client_to_call_missed_status_set_next_call_and_return,
    set_client_to_decline_status_and_return,
    set_client_to_phone_unavailable_status_and_return,
    set_client_to_promo_given_status_and_return,
    set_client_to_waiting_status_and_return,
    set_offer_already_published_by_offer_id,
    set_offer_cancelled_by_offer_id,
    set_offers_call_interrupted_by_client,
    set_offers_call_later_by_client,
    set_offers_call_missed_by_client,
    set_offers_declined_by_client,
    set_offers_in_progress_by_client,
    set_offers_phone_unavailable_by_client,
    set_offers_promo_given_by_client,
)
from external_offers.repositories.postgresql.clients import get_client_unactivated_by_client_id
from external_offers.repositories.postgresql.operators import get_operator_by_id, get_operator_team_id
from external_offers.repositories.postgresql.teams import get_team_by_id
from external_offers.services.operator_roles import get_operator_roles
from external_offers.utils import get_next_call_date_when_call_missed


logger = logging.getLogger(__name__)


async def update_offers_list(request: AdminUpdateOffersListRequest, user_id: int) -> AdminResponse:
    """ Обновить для оператора список объявлений в работе в админке """
    exists = await exists_offers_in_progress_by_operator(
        operator_id=user_id,
    )
    if exists:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Есть объявления в работе, завершите их',
                    code='offersInProgressExist'
                )
            ]
        )

    operator_roles = []
    operator_roles = await get_operator_roles(operator_id=user_id)
    operator_team_id = await get_operator_team_id(operator_id=user_id)
    async with pg.get().transaction():
        call_id = generate_guid()
        client_id = await assign_suitable_client_to_operator(
            operator_id=user_id,
            operator_team_id=operator_team_id,
            call_id=call_id,
            operator_roles=operator_roles,
            is_test=request.is_test,
        )
        if not client_id:
            return AdminResponse(
                success=False,
                errors=[
                    AdminError(
                        message='Отсутствуют доступные задания',
                        code='suitableClientMissing'
                    )
                ]
            )
        if offers_ids := await set_offers_in_progress_by_client(
            client_id=client_id,
            call_id=call_id,
        ):
            
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                operator_user_id=user_id,
                status=OfferStatus.in_progress.value,
                call_id=call_id
            )
    return AdminResponse(success=True, errors=[])


async def delete_offer(
    request: AdminDeleteOfferRequest,
    user_id: int
) -> AdminResponse:
    """ Удалить объявление в списке объявлений в админке """
    offer_id = request.offer_id
    client_id = request.client_id
    client = await get_client_by_client_id(client_id=request.client_id)
    if not client:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Пользователь с переданным идентификатором не найден',
                    code='missingUser'
                )
            ]
        )

    offer = await get_offer_by_offer_id(offer_id=offer_id)
    if not offer:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Объявление с переданным идентификатором не найдено',
                    code='missingOffer'
                )
            ]
        )
    async with pg.get().transaction():
        await set_offer_cancelled_by_offer_id(
            offer_id=offer_id
        )
        await save_event_log_for_offers(
            offers_ids=[offer_id],
            call_id=offer.last_call_id,
            operator_user_id=user_id,
            status=OfferStatus.cancelled.value
        )
        exists = await exists_offers_in_progress_by_client(
            client_id=client_id
        )
        if not exists:
            await set_client_to_status_and_send_kafka_message(
                client=client,
                offer=offer,
                set_client_to_status=set_client_to_waiting_status_and_return,
            )
    return AdminResponse(success=True, errors=[])


async def already_published_offer(
    request: AdminDeleteOfferRequest,
    user_id: int
) -> AdminResponse:
    """ Отметить объявление как уже опубликованное в админке """
    offer_id = request.offer_id
    client_id = request.client_id

    client = await get_client_by_client_id(client_id=request.client_id)
    if not client:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Пользователь с переданным идентификатором не найден',
                    code='missingUser'
                )
            ]
        )

    offer = await get_offer_by_offer_id(offer_id=offer_id)
    if not offer:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Объявление с переданным идентификатором не найдено',
                    code='missingOffer'
                )
            ]
        )

    async with pg.get().transaction():
        await set_offer_already_published_by_offer_id(
            offer_id=offer_id
        )

        await save_event_log_for_offers(
            offers_ids=[offer_id],
            call_id=offer.last_call_id,
            operator_user_id=user_id,
            status=OfferStatus.already_published.value
        )
        exists = await exists_offers_in_progress_by_client(
            client_id=client_id
        )
        if not exists:
            await set_client_to_status_and_send_kafka_message(
                client=client,
                offer=offer,
                set_client_to_status=set_client_to_waiting_status_and_return,
            )
    return AdminResponse(success=True, errors=[])


async def set_decline_status_for_client(
    request: AdminDeclineClientRequest,
    user_id: int
) -> AdminResponse:
    """ Поставить клиенту статус `Отклонен` в админке """
    client_id = request.client_id
    client = await get_client_by_client_id(client_id=request.client_id)
    if not client:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Пользователь с переданным идентификатором не найден',
                    code='missingUser'
                )
            ]
        )

    async with pg.get().transaction():

        if offers_ids := await set_offers_declined_by_client(
            client_id=client_id
        ):
            offer = await get_offer_by_offer_id(offer_id=offers_ids[0])
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                call_id=offer.last_call_id,
                operator_user_id=user_id,
                status=OfferStatus.declined.value
            )
            await set_client_to_status_and_send_kafka_message(
                client=client,
                offer=offer,
                set_client_to_status=set_client_to_decline_status_and_return,
                non_draft_status=CallStatus.declined,
            )

    return AdminResponse(success=True, errors=[])


async def set_call_interrupted_status_for_client(
    request: AdminCallInterruptedClientRequest,
    user_id: int
) -> AdminResponse:
    """ Поставить клиенту статус `Бросил трубку` в админке """
    client_id = request.client_id
    client = await get_client_by_client_id(client_id=request.client_id)
    if not client:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Пользователь с переданным идентификатором не найден',
                    code='missingUser'
                )
            ]
        )

    async with pg.get().transaction():

        if offers_ids := await set_offers_call_interrupted_by_client(
            client_id=client_id
        ):
            offer = await get_offer_by_offer_id(offer_id=offers_ids[0])
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                call_id=offer.last_call_id,
                operator_user_id=user_id,
                status=OfferStatus.call_interrupted.value
            )
            await set_client_to_status_and_send_kafka_message(
                client=client,
                offer=offer,
                set_client_to_status=set_client_to_call_interrupted_status_and_return,
                non_draft_status=CallStatus.call_interrupted,
            )

    return AdminResponse(success=True, errors=[])


async def set_phone_unavailable_status_for_client(
    request: AdminPhoneUnavailableClientRequest,
    user_id: int
) -> AdminResponse:
    """ Поставить клиенту статус `Бросил трубку` в админке """
    client_id = request.client_id
    client = await get_client_by_client_id(client_id=request.client_id)
    if not client:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Пользователь с переданным идентификатором не найден',
                    code='missingUser'
                )
            ]
        )

    async with pg.get().transaction():

        if offers_ids := await set_offers_phone_unavailable_by_client(
            client_id=client_id
        ):
            offer = await get_offer_by_offer_id(offer_id=offers_ids[0])
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                call_id=offer.last_call_id,
                operator_user_id=user_id,
                status=OfferStatus.phone_unavailable.value
            )
            await set_client_to_status_and_send_kafka_message(
                client=client,
                offer=offer,
                set_client_to_status=set_client_to_phone_unavailable_status_and_return,
                non_draft_status=CallStatus.phone_unavailable,
            )

    return AdminResponse(success=True, errors=[])


async def set_promo_given_status_for_client(
    request: AdminPromoGivenClientRequest,
    user_id: int
) -> AdminResponse:
    """ Поставить клиенту статус `Выдан промокод` в админке """
    client_id = request.client_id
    client = await get_client_by_client_id(client_id=request.client_id)
    if not client:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Пользователь с переданным идентификатором не найден',
                    code='missingUser'
                )
            ]
        )

    async with pg.get().transaction():
        if offers_ids := await set_offers_promo_given_by_client(
            client_id=client_id
        ):
            offer = await get_offer_by_offer_id(offer_id=offers_ids[0])
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                call_id=offer.last_call_id,
                operator_user_id=user_id,
                status=OfferStatus.promo_given.value
            )
            await set_client_to_status_and_send_kafka_message(
                client=client,
                offer=offer,
                set_client_to_status=set_client_to_promo_given_status_and_return,
                non_draft_status=CallStatus.promo_given,
            )

    return AdminResponse(success=True, errors=[])


async def set_call_missed_status_for_client(
    request: AdminCallMissedClientRequest,
    user_id: int
) -> AdminResponse:
    """ Поставить клиенту статус `Недозвон` в админке """
    client_id = request.client_id
    client = await get_client_by_client_id(client_id=request.client_id)

    if not client:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Пользователь с переданным идентификатором не найден',
                    code='missingUser'
                )
            ]
        )

    async with pg.get().transaction():
        next_call = get_next_call_date_when_call_missed(
            calls_count=client.calls_count
        )
        await set_client_to_call_missed_status_set_next_call_and_return(
            client_id=client_id,
            next_call=next_call
        )
        team_settings = {}
        team_id = None
        operator = await get_operator_by_id(user_id)
        if operator:
            team = await get_team_by_id(operator.team_id)
            if team:
                team_settings = team.get_settings()
                team_id = team.team_id
        if offers_ids := await set_offers_call_missed_by_client(
            client_id=client_id,
            team_settings=team_settings,
            team_id=team_id,
        ):
            offer = await get_offer_by_offer_id(offer_id=offers_ids[0])
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                call_id=offer.last_call_id,
                operator_user_id=user_id,
                status=OfferStatus.call_missed.value
            )

            await send_kafka_calls_analytics_message_if_not_test(
                client=client,
                offer=offer,
                status=CallStatus.call_missed,
            )

    return AdminResponse(success=True, errors=[])


async def set_call_later_status_for_client(
    request: AdminCallLaterClientRequest,
    user_id: int
) -> AdminResponse:
    """ Поставить клиенту статус `Позвонить позже` в админке """
    client_id = request.client_id
    call_later_datetime = request.call_later_datetime
    client = await get_client_by_client_id(client_id=request.client_id)
    if not client:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Пользователь с переданным идентификатором не найден',
                    code='missingUser'
                )
            ]
        )

    async with pg.get().transaction():

        await set_client_to_call_later_status_set_next_call_and_return(
            client_id=client_id,
            next_call=call_later_datetime
        )
        team_settings = {}
        team_id = None
        operator = await get_operator_by_id(user_id)
        if operator:
            team = await get_team_by_id(operator.team_id)
            if team:
                team_settings = team.get_settings()
                team_id = team.team_id
        if offers_ids := await set_offers_call_later_by_client(
            client_id=client_id,
            team_settings=team_settings,
            team_id=team_id,
        ):
            offer = await get_offer_by_offer_id(offer_id=offers_ids[0])
            client = await get_client_by_client_id(client_id=request.client_id)
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                call_id=offer.last_call_id,
                operator_user_id=user_id,
                status=OfferStatus.call_later.value
            )

            await send_kafka_calls_analytics_message_if_not_test(
                client=client,
                offer=offer,
                status=CallStatus.call_later,
            )
    return AdminResponse(success=True, errors=[])


async def set_client_to_status_and_send_kafka_message(
    *,
    client: Client,
    offer: Offer,
    set_client_to_status: Callable,
    non_draft_status: Optional[CallStatus] = None,
):
    created_draft = await exists_offers_draft_by_client(
        client_id=client.client_id
    )

    if created_draft:
        await set_client_accepted_and_no_operator_if_no_offers_in_progress(
            client_id=client.client_id
        )
        await send_kafka_calls_analytics_message_if_not_test(
            client=client,
            offer=offer,
            status=CallStatus.accepted,
        )
    else:
        await set_client_to_status(
            client_id=client.client_id
        )
        if non_draft_status:
            await send_kafka_calls_analytics_message_if_not_test(
                client=client,
                offer=offer,
                status=non_draft_status,
            )
