from external_offers.entities.teams import (
	UpdateOperatorTeamRequest,
	UpdateOperatorTeamResponse,
)


async def check_if_teamlead(user_id):
	# TODO: Затащить проверку на роль
	return True


async def update_operator_team(request: UpdateOperatorTeamRequest, user_id: int) -> UpdateOperatorTeamResponse:
	is_teamlead = check_if_teamlead(user_id)
	if not is_teamlead:
	    return UpdateOperatorTeamResponse(success=False, message="Вы не тимлид")
	team_id = request.team_id
	operator_id = request.operator_id
