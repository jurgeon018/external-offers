from external_offers.entities import (
    UpdateClientAdditionalEmailsRequest,
    UpdateClientAdditionalEmailsResponse,
)
from external_offers.repositories.postgresql.clients import (
    get_client_by_client_id,
    set_additional_emails_by_client_id,
)


async def update_client_additional_emails_public(
    request: UpdateClientAdditionalEmailsRequest,
    user_id: int,
) -> UpdateClientAdditionalEmailsResponse:
    """ Обновить дополнительные номера клиента """
    client_id = request.client_id
    additional_emails = request.additionalEmails

    client = await get_client_by_client_id(client_id=client_id)
    if not client:
        return UpdateClientAdditionalEmailsResponse(
            message='Такого клиента не существует.',
            success=False,
        )
    try:
        await set_additional_emails_by_client_id(
            client_id=client_id,
            additional_emails=additional_emails
        )
    except Exception as exc:
        return UpdateClientAdditionalEmailsResponse(
            message=f'Ошибка при обновлении дополнительных почт. {exc}',
            success=False,
        )

    return UpdateClientAdditionalEmailsResponse(
        message='Дополнительные почты были обновлены',
        success=True,
    )
