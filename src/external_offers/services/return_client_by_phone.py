from external_offers import pg
from external_offers.entities import ReturnClientByPhoneError, ReturnClientByPhoneRequest, ReturnClientByPhoneResponse
from external_offers.enums import ClientStatus, OfferStatus, ReturnClientByPhoneErrorCode
from external_offers.helpers.phonenumber import transform_phone_number_to_inner_format
from external_offers.helpers.uuid import generate_guid
from external_offers.repositories.postgresql import (
    assign_client_to_operator_and_increase_calls_count,
    get_client_for_update_by_phone_number,
    save_event_log_for_offers,
    set_undrafted_offers_in_progress_by_client,
)


SUITABLE_RETURN_CLIENT_STATUS = [
    ClientStatus.call_later,
    ClientStatus.call_missed,
    ClientStatus.waiting
]


async def return_client_by_phone(request: ReturnClientByPhoneRequest, user_id: int) -> ReturnClientByPhoneResponse:
    """ Взять в работу клиента по номеру телефона. Возможно не для всех статусов """
    phone_number = transform_phone_number_to_inner_format(request.phone_number)
    async with pg.get().transaction():
        client = await get_client_for_update_by_phone_number(
            phone_number=phone_number
        )

        if not client:
            return ReturnClientByPhoneResponse(
                success=False,
                errors=[
                    ReturnClientByPhoneError(
                        message='Клиент отсутствует или уже находится в работе',
                        code=ReturnClientByPhoneErrorCode.missing_client
                    )
                ]
            )

        if client.status not in SUITABLE_RETURN_CLIENT_STATUS:
            return ReturnClientByPhoneResponse(
                success=False,
                errors=[
                    ReturnClientByPhoneError(
                        message=f'Неподходящий статус клиента: {client.status.value}',
                        code=ReturnClientByPhoneErrorCode.wrong_status
                    )
                ]
            )

        call_id = generate_guid()
        await assign_client_to_operator_and_increase_calls_count(
            client_id=client.client_id,
            operator_id=user_id
        )
        if offers_ids := await set_undrafted_offers_in_progress_by_client(
            client_id=client.client_id,
            call_id=call_id
        ):
            await save_event_log_for_offers(
                offers_ids=offers_ids,
                operator_user_id=user_id,
                status=OfferStatus.in_progress.value,
                call_id=call_id
            )

    return ReturnClientByPhoneResponse(success=True, errors=[])
