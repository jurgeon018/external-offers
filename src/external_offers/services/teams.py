from asyncpg.exceptions import PostgresError, UniqueViolationError

from external_offers.entities.response import BasicResponse
from external_offers.entities.teams import CreateTeamRequest, DeleteTeamRequest, UpdateTeamRequest
from external_offers.helpers.uuid import generate_guid
from external_offers.repositories.postgresql.teams import create_team, delete_team_by_id, update_team_by_id


async def create_team_public(request: CreateTeamRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        id = generate_guid()
        await create_team(
            id=id,
            name=request.name,
            lead_id=request.lead_id,
            segment=getattr(request.segment, 'value', None),
        )
        success = True
        message = 'Команда была успешно создана.'
    except UniqueViolationError as e:
        message = f'Такая команда уже существует: {e}'
    except PostgresError as e:
        message = f'Во время создания команды произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )


async def update_team_public(request: UpdateTeamRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        await update_team_by_id(
            id=request.id,
            name=request.name,
            lead_id=request.lead_id,
            segment=getattr(request.segment, 'value', None),
        )
        success = True
        message = 'Информация про команду была успешно обновлена.'
    except PostgresError as e:
        message = f'Во время обновления команды произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )


async def delete_team_public(request: DeleteTeamRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        await delete_team_by_id(id=request.id)
        success = True
        message = 'Команда была успешно удалена.'
    except PostgresError as e:
        message = f'Во время удаления команды произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )
