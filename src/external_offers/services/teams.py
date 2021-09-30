from asyncpg.exceptions import PostgresError, UniqueViolationError

from external_offers.entities.response import BasicResponse
from external_offers.entities.teams import CreateTeamRequest, DeleteTeamRequest, UpdateTeamRequest, TeamSettings
from external_offers.repositories.postgresql.teams import create_team, delete_team_by_id, update_team_by_id
from cian_core.runtime_settings import runtime_settings
from dataclasses import asdict

async def create_team_public(request: CreateTeamRequest, user_id: int) -> BasicResponse:
    success = False
    settings = asdict(TeamSettings(
        categories=[],
        regions=[],
        segments=[],
        subsegments=[],
        promocode_regions=[],
        filling=[],              
        main_regions_priority=runtime_settings.MAIN_REGIONS_PRIORITY,
    ))
    try:
        await create_team(
            team_name=request.team_name,
            lead_id=request.lead_id,
            settings=settings,
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
    team_id = request.team_id
    team_name = request.team_name
    lead_id = request.lead_id
    settings = asdict(request)
    del settings['team_id']
    del settings['team_name']
    del settings['lead_id']
    print()
    print('request', request)
    print()
    try:
        await update_team_by_id(
            team_id=team_id,
            team_name=team_name,
            lead_id=lead_id,
            settings=settings,
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
        await delete_team_by_id(team_id=request.team_id)
        success = True
        message = 'Команда была успешно удалена.'
    except PostgresError as e:
        message = f'Во время удаления команды произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )
