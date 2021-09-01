from external_offers.repositories.postgresql.teams import (
	create_team,
    operator_with_id_exists,
    create_operator,
    update_operator_name_by_id,
	# update_operator_team,
	# update_team_segment,
)
from external_offers.entities.teams import (
    UpdateOperatorNameRequest,
    UpdateOperatorNameResponse,
	CreateTeamRequest,
	CreateTeamResponse,
	# UpdateOperatorTeamRequest,
	# UpdateOperatorTeamResponse,
	# UpdateTeamSegmentRequest,
	# UpdateTeamSegmentResponse,
)


async def operator_name_public(request: UpdateOperatorNameRequest, user_id) -> UpdateOperatorNameResponse:
    name = request.name
    exists = await operator_with_id_exists(user_id)
    if exists:
        await create_operator(
            id=user_id,
            name=name,
        )
    else:
        await update_operator_name_by_id(name)
		# TO DO: сделать так чтобы менеджер мог сам себя перекинуть в другую команду  
        # team_id = request.team_id
    return UpdateOperatorNameResponse(
        success=True,
        message='',
    )


async def create_team_public(request: CreateTeamRequest, user_id: int) -> CreateTeamResponse:
    name = request.name
    await create_team(name)
    return CreateTeamResponse(
        success=True,
        message="Команда была успешно создана.",
    )


async def update_team_name_public(request: UpdateTeamNameRequest, user_id: int) -> UpdateTeamNameResponse:
    name = request.name
    team_id = request.team_id
    await update_team_name_by_team_id(
        name=name,
        id=team_id
    )
    return UpdateTeamNameResponse(
        success=True,
        message='Название команды было успешно обновлено',
    )


# async def update_operators_team_public(request: UpdateOperatorsTeamRequest, user_id: int) -> updateOperatorsTeamResponse:
#     await update_operators_team()
# 	return UpdateOperatorsTeamResponse(
#         success=True,
#         message='Состав команды был успешно изменен',
#     )


# async def update_team_settings_public(request: UpdateTeamSettingsRequest, user_id: int) -> UpdateTeamSettingsResponse:
#     await update_team_settings()
# 	return UpdateTeamSettingsResponse(
#         success=True,
#         message='Настройки команды были успешно изменены.',
#     )



# async def update_operator_team_public(request: UpdateOperatorTeamRequest, user_id: int) -> UpdateOperatorTeamResponse:
# 	# if not (await check_if_teamlead(user_id)):
# 	#     return UpdateOperatorTeamResponse(success=False, message="Вы должны обладать правами тимлида для выполнения этого действия.")
# 	operator_id = request.operator_id
# 	team_id = request.team_id
# 	await update_operator_team(
# 		operator_id=operator_id,
# 		team_id=team_id,
# 	)
# 	return UpdateOperatorTeamResponse(
# 		success=True,
# 		message="",
# 	)


# async def update_team_segment_public(request: UpdateTeamSegmentRequest, user_id: int) -> UpdateTeamSegmentResponse:
# 	# if not check_if_teamlead(user_id):
# 	#     return UpdateOperatorTeamResponse(success=False, message="Вы должны обладать правами тимлида для выполнения этого действия.")
# 	team_id = request.team_id
# 	segment = request.segment
# 	await update_team_segment(
# 		team_id=team_id,
# 		segment=segment,
# 	)
# 	return UpdateTeamSegmentResponse(
# 		success=True,
# 		message="",
# 	)

