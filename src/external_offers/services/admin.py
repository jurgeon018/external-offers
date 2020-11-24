from external_offers import pg
from external_offers.entities.admin import (
    AdminCallMissedClientRequest,
    AdminDeclineClientRequest,
    AdminDeleteOfferRequest,
    AdminError,
    AdminResponse,
)
from external_offers.enums import OfferStatus
from external_offers.repositories.postgresql import (
    assign_waiting_client_to_operator,
    exists_offers_in_progress_by_client,
    exists_offers_in_progress_by_operator,
    exists_waiting_client,
    save_event_log_for_offers,
    set_client_to_call_missed_status,
    set_client_to_decline_status,
    set_client_to_waiting_status,
    set_offer_cancelled_by_offer_id,
    set_offers_call_missed_by_client,
    set_offers_declined_by_client,
    set_waiting_offers_in_progress_by_client,
)


async def update_offers_list(user_id: int) -> AdminResponse:
    """ Обновить лист объявлений в админке """
    exists_client = await exists_waiting_client()

    if not exists_client:
        return AdminResponse(
            success=False,
            errors=[AdminError(
                message='Отсутствуют доступные задания',
                code='waitingClientMissing'
            )])



    exists = await exists_offers_in_progress_by_operator(user_id)
    if exists:
        return AdminResponse(
            success=False,
            errors=[AdminError(
                message='Есть объявления в работе, завершите их',
                code='offersInProgressExist'
            )])

    async with pg.get().transaction():
        client_id = await assign_waiting_client_to_operator(user_id)
        if offers_ids := await set_waiting_offers_in_progress_by_client(client_id):
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                operator_user_id=user_id,
                status=OfferStatus.in_progress.value
            )

    return AdminResponse(success=True, errors=[])


async def delete_offer(request: AdminDeleteOfferRequest, user_id: int) -> AdminResponse:
    """ Удалитть объявление в списке объявлений в админке """
    offer_id = request.offer_id
    client_id = request.client_id

    async with pg.get().transaction():
        await set_offer_cancelled_by_offer_id(offer_id)
        await save_event_log_for_offers(
            offers_ids=[offer_id],
            operator_user_id=user_id,
            status=OfferStatus.cancelled.value
        )
        exists = await exists_offers_in_progress_by_client(client_id)

        if not exists:
            await set_client_to_waiting_status(client_id)

    return AdminResponse(success=True, errors=[])


async def set_decline_status_for_client(request: AdminDeclineClientRequest, user_id: int) -> AdminResponse:
    """ Поставить клиенту статус `Отклонен` в админке """
    client_id = request.client_id

    async with pg.get().transaction():
        await set_client_to_decline_status(client_id)

        if offers_ids := await set_offers_declined_by_client(client_id):
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                operator_user_id=user_id,
                status=OfferStatus.declined.value
            )

    return AdminResponse(success=True, errors=[])


async def set_call_missed_status_for_client(request: AdminCallMissedClientRequest, user_id: int) -> AdminResponse:
    """ Поставить клиенту статус `Недозвон` в админке """
    client_id = request.client_id

    async with pg.get().transaction():
        await set_client_to_call_missed_status(client_id)
        if offers_ids := await set_offers_call_missed_by_client(client_id):
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                operator_user_id=user_id,
                status=OfferStatus.call_missed.value
            )

    return AdminResponse(success=True, errors=[])
