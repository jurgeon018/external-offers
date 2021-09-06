from asyncpg.exceptions import PostgresError, UniqueViolationError
from external_offers.entities.response import BasicResponse
from external_offers.entities.operators import (
    CreateOperatorRequest,
    UpdateOperatorRequest,
    DeleteOperatorRequest,
)
from external_offers.repositories.postgresql.operators import (
    create_operator,
    update_operator_by_id,
    delete_operator_by_id,
)


async def create_operator_public(request: CreateOperatorRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        await create_operator(
            id=request.id,
            name=request.name,
            team_id=request.team_id,
        )
        message = "Оператор был успешно создан."
        success = True
    except UniqueViolationError as e:
        message = f'Такой оператор уже существует: {e}'
    except PostgresError as e:
        message = f'Во время создания оператора произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )


async def update_operator_public(request: UpdateOperatorRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        await update_operator_by_id(
            id=request.id,
            name=request.name,
            team_id=request.team_id,
        )
        message = 'Персональная информация про оператора была успешно изменена.'
        success = True
    except PostgresError as e:
        message = f'Во время обновления оператора произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message
    )


async def delete_operator_public(request: DeleteOperatorRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        await delete_operator_by_id(id=request.id)
        success = True
        message='Оператор был успешно удален.'
    except PostgresError as e:
        message = f'Во время удаления оператора произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )
