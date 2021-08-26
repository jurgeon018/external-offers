from typing import List, NoReturn

import backoff
from cian_core.degradation import DegradationResult, get_degradation_handler
from cian_core.runtime_settings import runtime_settings

from external_offers.helpers.errors import USER_ROLES_REQUEST_MAX_TRIES_ERROR, DegradationException
from external_offers.repositories.users import v1_get_user_roles
from external_offers.repositories.users.entities import GetUserRolesResponse, V1GetUserRoles


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
