from external_offers.entities import UpdateClientReasonOfDeclineResponse, UpdateClientReasonOfDeclineRequest
from external_offers.repositories.postgresql.clients import (
    get_client_by_client_id,
    set_reason_of_decline_by_client_id,
)


async def update_client_reason_of_decline_public(
    request: UpdateClientReasonOfDeclineRequest,
    user_id: int,
) -> UpdateClientReasonOfDeclineResponse:
    """ Обновить причину отказа клиента """
    client_id = request.client_id

    client = await get_client_by_client_id(client_id=client_id)
    if not client:
        return UpdateClientReasonOfDeclineResponse(
            message='Такого клиента не существует.',
            success=False,
        )
    try:
        print('request.reason_of_decline', request.reasonOfDecline)
        await set_reason_of_decline_by_client_id(
            client_id=client_id,
            reason_of_decline=request.reasonOfDecline.value if request.reasonOfDecline else None
        )
    except Exception as exc:
        return UpdateClientReasonOfDeclineResponse(
            message=f'Ошибка при обновлении причины отказа. {exc}',
            success=False,
        )

    return UpdateClientReasonOfDeclineResponse(
        message='Причина отказа была обновлена',
        success=True,
    )
