from external_offers.entities import BasicResponse
from external_offers.entities.update_client_real_info import UpdateClientRealInfoRequest
from external_offers.repositories.postgresql.clients import get_client_by_client_id, set_real_info_by_client_id


async def update_client_real_info_public(request: UpdateClientRealInfoRequest, user_id: int) -> BasicResponse:
    client_id = request.client_id

    if not await get_client_by_client_id(client_id=client_id):
        return BasicResponse(
            success=False,
            message='Пользователь с переданным идентификатором не найден',
        )

    real_phone = request.real_phone
    if real_phone and len(real_phone) != 11:
        return BasicResponse(
            success=False,
            message='Номер телефона должен состоять из 11ти символов.',
        )
    if real_phone and not real_phone.startswith(('7', '8')):
        return BasicResponse(
            success=False,
            message='Номер телефона должен начинаться с символа 7 или 8.',
        )
    await set_real_info_by_client_id(
        client_id=client_id,
        real_phone=real_phone,
        real_phone_hunted_at=request.real_phone_hunted_at,
        real_name=request.real_name,
    )
    return BasicResponse(
        success=True,
        message='Реальные данные клиента были успешно изменены'
    )
