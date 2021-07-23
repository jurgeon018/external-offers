from external_offers.entities import UpdateClientCommentRequest, UpdateClientCommentResponse
from external_offers.repositories.postgresql.clients import get_client_by_client_id, set_comment_by_client_id


async def update_client_comment_public(
    request: UpdateClientCommentRequest, user_id: int
) -> UpdateClientCommentResponse:
    """ Обновить комментарий к карточке клиента """
    client_id = request.client_id
    comment = request.comment

    client = await get_client_by_client_id(client_id=client_id)
    if not client:
        return UpdateClientCommentResponse(
            message = 'Такого клиента не существует.',
            success=False,
        )
    try:
        await set_comment_by_client_id(
            client_id=client_id,
            comment=comment
        )
    except Exception as exc:
        return UpdateClientCommentResponse(
            message=f'Ошибка при обновлении коментария. {exc}',
            success=False,
        )


    return UpdateClientCommentResponse(
        message='Коментарий к карточке клиента был обновлен.',
        success=True,
    )
