from external_offers.entities import BasicResponse
from external_offers.entities.update_client_real_phone import UpdateClientRealInfoRequest
from external_offers.repositories.postgresql.clients import get_client_by_client_id, set_real_info_by_client_id


async def update_client_real_info_public(request: UpdateClientRealInfoRequest, user_id: int) -> BasicResponse:
    client_id = request.client_id
    real_phone = request.real_phone
    real_phone_hunted_at = request.real_phone_hunted_at
    real_name = request.real_name

    client = await get_client_by_client_id(client_id=client_id)
    if not client:
        return BasicResponse(
            success=False,
            message='Пользователь с переданным идентификатором не найден',
        )

    await set_real_info_by_client_id(
        client_id=client_id,
        real_phone=real_phone,
        real_phone_hunted_at=real_phone_hunted_at,
        real_name=real_name,
    )
    return BasicResponse(
        success=True,
        message='Реальные данные клиента были успешно изменены'
    )
