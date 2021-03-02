import logging

from external_offers import pg
from external_offers.entities.admin import (
    AdminCallMissedClientRequest,
    AdminDeclineClientRequest,
    AdminDeleteOfferRequest,
    AdminError,
    AdminResponse,
)
from external_offers.enums import ClientStatus, OfferStatus
from external_offers.helpers.uuid import generate_guid
from external_offers.queue.helpers import send_kafka_calls_analytics_message_if_not_test
from external_offers.repositories.postgresql import (
    assign_waiting_client_to_operator,
    exists_offers_draft_by_client,
    exists_offers_in_progress_by_client,
    exists_offers_in_progress_by_operator,
    exists_waiting_client,
    get_client_by_client_id,
    get_offer_by_offer_id,
    save_event_log_for_offers,
    set_client_accepted_and_no_operator_if_no_offers_in_progress,
    set_client_to_call_later_status_and_return,
    set_client_to_call_missed_status_and_return,
    set_client_to_decline_status_and_return,
    set_client_to_waiting_status_and_return,
    set_offer_cancelled_by_offer_id,
    set_offers_call_later_by_client,
    set_offers_call_missed_by_client,
    set_offers_declined_by_client,
    set_waiting_offers_in_progress_by_client,
)


logger = logging.getLogger(__name__)


async def update_offers_list(user_id: int) -> AdminResponse:
    """ Обновить для оператора список объявлений в работе в админке """
    exists_client = await exists_waiting_client()

    if not exists_client:
        return AdminResponse(
            success=False,
            errors=[
                AdminError(
                    message='Отсутствуют доступные задания',
                    code='waitingClientMissing'
                )
            ]
        )

    exists = await exists_offers_in_progress_by_operator(
        operator_id=user_id
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

    async with pg.get().transaction():
        call_id = generate_guid()
        client_id = await assign_waiting_client_to_operator(
            operator_id=user_id
        )
        if offers_ids := await set_waiting_offers_in_progress_by_client(
            client_id=client_id,
            call_id=call_id
        ):
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                operator_user_id=user_id,
                status=OfferStatus.in_progress.value,
                call_id=call_id
            )

    return AdminResponse(success=True, errors=[])


async def delete_offer(request: AdminDeleteOfferRequest, user_id: int) -> AdminResponse:
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
            created_draft = await exists_offers_draft_by_client(
                client_id=client_id
            )

            if created_draft:
                await set_client_accepted_and_no_operator_if_no_offers_in_progress(
                    client_id=client_id
                )
                await send_kafka_calls_analytics_message_if_not_test(
                    client=client,
                    offer=offer,
                    status=ClientStatus.accepted,
                )
            else:
                await set_client_to_waiting_status_and_return(
                    client_id=client_id
                )

    return AdminResponse(success=True, errors=[])


async def set_decline_status_for_client(request: AdminDeclineClientRequest, user_id: int) -> AdminResponse:
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
        created_draft = await exists_offers_draft_by_client(
            client_id=client_id
        )

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

            if created_draft:
                await send_kafka_calls_analytics_message_if_not_test(
                    client=client,
                    offer=offer,
                    status=ClientStatus.accepted,
                )
                await set_client_accepted_and_no_operator_if_no_offers_in_progress(
                    client_id=client_id
                )
            else:
                await send_kafka_calls_analytics_message_if_not_test(
                    client=client,
                    offer=offer,
                    status=ClientStatus.declined,
                )
                await set_client_to_decline_status_and_return(
                    client_id=client_id
                )

    return AdminResponse(success=True, errors=[])


async def set_call_missed_status_for_client(request: AdminCallMissedClientRequest, user_id: int) -> AdminResponse:
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
        await set_client_to_call_missed_status_and_return(
            client_id=client_id
        )

        if offers_ids := await set_offers_call_missed_by_client(
            client_id=client_id
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
                status=ClientStatus.call_missed,
            )

    return AdminResponse(success=True, errors=[])


async def set_call_later_status_for_client(request: AdminCallMissedClientRequest, user_id: int) -> AdminResponse:
    """ Поставить клиенту статус `Позвонить позже` в админке """
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
        await set_client_to_call_later_status_and_return(
            client_id=client_id
        )
        if offers_ids := await set_offers_call_later_by_client(
            client_id=client_id
        ):
            offer = await get_offer_by_offer_id(offer_id=offers_ids[0])
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                call_id=offer.last_call_id,
                operator_user_id=user_id,
                status=OfferStatus.call_later.value
            )

            await send_kafka_calls_analytics_message_if_not_test(
                client=client,
                offer=offer,
                status=ClientStatus.call_later,
            )

    return AdminResponse(success=True, errors=[])
