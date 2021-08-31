from external_offers.repositories.postgresql.teams import (
	
)
from external_offers.entities.teams import (
	UpdateOperatorTeamRequest,
	UpdateOperatorTeamResponse,
	UpdateTeamRoleRequest,
	UpdateTeamRoleResponse,
	CreateTeamRequest,
	CreateTeamResponse,
)


async def check_if_teamlead(user_id):
	# TODO: Затащить проверку на роль
	return True


async def update_operator_team_public(request: UpdateOperatorTeamRequest, user_id: int) -> UpdateOperatorTeamResponse:
	if not (await check_if_teamlead(user_id)):
	    return UpdateOperatorTeamResponse(success=False, message="Вы должны обладать правами тимлида для выполнения этого действия.")
	team_id = request.team_id
	operator_id = request.operator_id
	return UpdateOperatorTeamResponse(
		success=True,
		message="",
	)


async def update_team_role_public(request: UpdateTeamRoleRequest, user_id: int) -> UpdateTeamRoleResponse:
	if not check_if_teamlead(user_id):
	    return UpdateOperatorTeamResponse(success=False, message="Вы должны обладать правами тимлида для выполнения этого действия.")
	team_id = request.team_id
	role_id = request.role_id
	return UpdateTeamRoleResponse(
		success=True,
		message="",
	)


async def create_team_public(request: CreateTeamRequest, user_id: int) -> CreateTeamResponse:
	if not check_if_teamlead(user_id):
	    return UpdateOperatorTeamResponse(success=False, message="Вы должны обладать правами тимлида для выполнения этого действия.")
	name = request.name
	return CreateTeamResponse(
		success=True,
		message="",
	)
