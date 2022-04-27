from asyncpg.exceptions import PostgresError, UniqueViolationError
from cian_http.exceptions import ApiClientException

from external_offers.entities.operators import (
    CreateOperatorRequest,
    DeleteOperatorRequest,
    UpdateOperatorRequest,
    UpdateOperatorsRequest,
)
from external_offers.entities.response import BasicResponse
from external_offers.queue.producers import operator_producer
from external_offers.repositories.postgresql.operators import (
    create_operator,
    delete_operator_by_id,
    update_operator_by_id,
)
from external_offers.services.operator_roles import add_operator_role_to_user, remove_operator_role, update_operators


async def create_operator_public(request: CreateOperatorRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        await add_operator_role_to_user(operator_id=request.operator_id)
        await create_operator(
            operator_id=request.operator_id,
            is_teamlead=False,
        )
        if error := await update_operators():
            message = f'Во время обновления списка пользователей произошла ошибка: {error}'
        else:
            message = 'Оператор был успешно создан.'
            success = True
    except ApiClientException as e:
        message = f'Во время создания оператора произошла ошибка: {e}'
    except UniqueViolationError as e:
        message = f'Такой оператор уже существует: {e}'
    except PostgresError as e:
        message = f'Во время создания оператора произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )


async def update_operators_public(request: UpdateOperatorsRequest, user_id: int) -> BasicResponse:
    """Обновить список пользователей"""
    success = True
    message = 'Список пользователей был успешно обновлен.'
    if error := await update_operators():
        success = False
        message = f'Во время обновления списка пользователей произошла ошибка: {error}'
    return BasicResponse(success=success, message=message)


async def update_operator_public(request: UpdateOperatorRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        operator = await update_operator_by_id(
            operator_id=request.operator_id,
            full_name=request.full_name,
            team_id=request.team_id,
            email=request.email,
        )
        message = 'Информация про оператора была успешно обновлена.'
        success = True
        await operator_producer(operator)
    except PostgresError as e:
        message = f'Во время обновления оператора произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message
    )


async def delete_operator_public(request: DeleteOperatorRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        await remove_operator_role(operator_id=request.operator_id)
        await delete_operator_by_id(operator_id=request.operator_id)
        success = True
        message = 'Оператор был успешно удален.'
    except ApiClientException as e:
        message = f'Во время удаления роли оператора произошла ошибка: {e.message}'
    except PostgresError as e:
        message = f'Во время удаления оператора произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )
