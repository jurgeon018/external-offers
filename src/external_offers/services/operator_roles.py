import logging
from typing import List, NoReturn, Optional, Union

import backoff
from cian_core.degradation import DegradationResult, get_degradation_handler
from cian_core.runtime_settings import runtime_settings
from cian_http.exceptions import ApiClientException

from external_offers.entities.operators import EnrichedOperator
from external_offers.helpers.errors import USER_ROLES_REQUEST_MAX_TRIES_ERROR, DegradationException
from external_offers.repositories.postgresql.operators import (
    create_operator,
    get_enriched_operator_by_id,
    update_operator_by_id,
)
from external_offers.repositories.users import v1_add_role_to_user, v1_get_user_roles, v1_remove_role_from_user
from external_offers.repositories.users._repo import v1_get_userids_by_rolename, v1_get_users, v1_user_has_role
from external_offers.repositories.users.entities import (
    AddRoleToUserRequest,
    GetUserIdsByRoleNameResponse,
    GetUserRolesResponse,
    GetUsersResponse,
    RemoveRoleFromUserRequest,
    UserIdsRequest,
    UserModel,
    V1GetUserRoles,
    V1GetUseridsByRolename,
    V1UserHasRole,
)


logger = logging.getLogger(__name__)


v1_get_user_roles_with_degradation = get_degradation_handler(
    func=v1_get_user_roles,
    default=GetUserRolesResponse(roles=[]),
    key='v1_get_user_roles',
)


def user_roles_request_give_up_callback(backoff_details: dict) -> NoReturn:
    agent_request = backoff_details['args'][0]
    realty_user_id = agent_request.user_id

    tries_count = backoff_details['tries']

    raise DegradationException(
        USER_ROLES_REQUEST_MAX_TRIES_ERROR % {
            'user_id': realty_user_id,
            'tries': tries_count,
        }
    )


def user_roles_request_retry_predicate(
    degradation_result: DegradationResult[GetUserRolesResponse]
) -> bool:
    return degradation_result.degraded


v1_get_user_roles_with_retries = backoff.on_predicate(
    backoff.expo,
    predicate=user_roles_request_retry_predicate,
    max_tries=runtime_settings.EXTERNAL_OFFERS_GET_USER_ROLES_TRIES_COUNT,
    on_giveup=user_roles_request_give_up_callback,
)(v1_get_user_roles_with_degradation)


async def get_operator_roles(operator_id: int) -> List[str]:
    request = V1GetUserRoles(user_id=operator_id)
    result: DegradationResult[GetUserRolesResponse] = await v1_get_user_roles_with_retries(request)
    return [role.name for role in result.value.roles]


async def get_or_create_operator(
    *,
    operator_id: Union[int, str],
    full_name: Optional[str] = None,
    team_id: Optional[int] = None,
    is_teamlead: bool = False,
    email: Optional[str] = None,
) -> EnrichedOperator:
    current_operator = await get_enriched_operator_by_id(operator_id=operator_id)
    if not current_operator:
        await create_operator(
            operator_id=operator_id,
            full_name=full_name,
            team_id=team_id,
            is_teamlead=is_teamlead,
            email=email,
        )
        current_operator = await get_enriched_operator_by_id(operator_id=operator_id)
    return current_operator


async def create_or_update_operator(
    *,
    operator_id: Union[int, str],
    full_name: Optional[str] = None,
    team_id: Optional[int] = None,
    is_teamlead: bool = False,
    email: Optional[str] = None,
) -> EnrichedOperator:
    current_operator = await get_enriched_operator_by_id(operator_id=operator_id)
    if not current_operator:
        await create_operator(
            operator_id=operator_id,
            full_name=full_name,
            team_id=team_id,
            is_teamlead=is_teamlead,
            email=email,
        )
    else:
        await update_operator_by_id(
            operator_id=operator_id,
            full_name=full_name,
            team_id=current_operator.team_id,
            is_teamlead=is_teamlead,
            email=email,
        )
    current_operator = await get_enriched_operator_by_id(operator_id=operator_id)
    return current_operator


async def remove_operator_role(operator_id: str) -> None:
    await v1_remove_role_from_user(
        RemoveRoleFromUserRequest(
            user_id=int(operator_id),
            role_name=runtime_settings.ADMIN_OPERATOR_ROLE,
        )
    )


async def add_operator_role_to_user(operator_id: str) -> None:
    await v1_add_role_to_user(
        AddRoleToUserRequest(
            user_id=int(operator_id),
            role_name=runtime_settings.ADMIN_OPERATOR_ROLE,
        )
    )


async def update_operators() -> Optional[str]:
    teamlead_role_name = runtime_settings.ADMIN_TEAMLEAD_ROLE
    admin_role_name = runtime_settings.ADMIN_OPERATOR_ROLE
    try:
        users = await get_users_by_role(role_name=admin_role_name)
    except ApiClientException as e:
        return str(e.message)
    for user in users:
        operator_id = user.id  # or user.cian_user_id
        if operator_id:
            try:
                is_teamlead: bool = await v1_user_has_role(
                    V1UserHasRole(
                        user_id=int(operator_id),
                        role_name=teamlead_role_name,
                        use_cache=None,
                    )
                )
            except ApiClientException as e:
                return str(e.message)
            if user.user_name:
                full_name = user.user_name
            elif user.first_name and user.last_name:
                full_name = f'{user.first_name} {user.last_name}'
            else:
                full_name = None
            email = user.email
            await create_or_update_operator(
                operator_id=operator_id,
                full_name=full_name,
                team_id=None,
                is_teamlead=is_teamlead,
                email=email,
            )


async def get_users_by_role(role_name: str) -> List[UserModel]:
    user_ids_response: GetUserIdsByRoleNameResponse = await v1_get_userids_by_rolename(
        V1GetUseridsByRolename(
            role_name=role_name
        )
    )
    user_ids: List[int] = user_ids_response.user_ids
    if not user_ids:
        return []
    users_response: GetUsersResponse = await v1_get_users(
        UserIdsRequest(
            user_ids=user_ids
        )
    )
    users: List[UserModel] = users_response.users
    return users
