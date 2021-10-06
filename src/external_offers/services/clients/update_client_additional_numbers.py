from external_offers.entities import (
    UpdateClientAdditionalNumbersRequest,
    UpdateClientAdditionalNumbersResponse,
)
from external_offers.repositories.postgresql.clients import (
    get_client_by_client_id,
    set_additional_numbers_by_client_id,
)


async def update_client_additional_numbers_public(
    request: UpdateClientAdditionalNumbersRequest,
    user_id: int,
) -> UpdateClientAdditionalNumbersResponse:
    """ Обновить дополнительные номера клиента """
    client_id = request.client_id
    additional_numbers = request.additionalNumbers

    client = await get_client_by_client_id(client_id=client_id)
    if not client:
        return UpdateClientAdditionalNumbersResponse(
            message='Такого клиента не существует.',
            success=False,
        )
    try:
        await set_additional_numbers_by_client_id(
            client_id=client_id,
            additional_numbers=additional_numbers
        )
    except Exception as exc:
        return UpdateClientAdditionalNumbersResponse(
            message=f'Ошибка при обновлении дополнительных номеров. {exc}',
            success=False,
        )

    return UpdateClientAdditionalNumbersResponse(
        message='Дополнительные тел. номера были обновлены',
        success=True,
    )
