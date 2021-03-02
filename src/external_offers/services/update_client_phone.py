from external_offers.entities import UpdateClientPhoneError, UpdateClientPhoneRequest, UpdateClientPhoneResponse
from external_offers.enums import UpdateClientPhoneErrorCode
from external_offers.repositories.postgresql import get_client_by_client_id, set_phone_number_by_client_id


async def update_client_phone_public(request: UpdateClientPhoneRequest, user_id: int) -> UpdateClientPhoneResponse:
    """ Обновить телефон клиента """
    client_id = request.client_id
    phone_number = request.phone_number

    client = await get_client_by_client_id(client_id=client_id)
    if not client:
        return UpdateClientPhoneResponse(
            success=False,
            errors=[
                UpdateClientPhoneError(
                    message='Пользователь с переданным идентификатором не найден',
                    code=UpdateClientPhoneErrorCode.missing_client
                )
            ]
        )

    await set_phone_number_by_client_id(
        client_id=client_id,
        phone_number=phone_number
    )

    return UpdateClientPhoneResponse(success=True, errors=[])
