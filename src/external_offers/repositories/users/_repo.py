# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client users`

cian-codegen version: 1.16.3

"""
from cian_http.api_client import Api

from . import entities

_api = Api(microservice_name='users')
v1_add_role_to_user = _api.make_client(path='/v1/add-role-to-user/', method
    ='POST', handle_http_exceptions=True, request_schema=entities.
    AddRoleToUserRequest)
v1_get_realty_id = _api.make_client(path='/v1/get-realty-id/', method='GET',
    handle_http_exceptions=True, request_schema=entities.V1GetRealtyId,
    response_schema=int)
v1_get_user_roles = _api.make_client(path='/v1/get-user-roles/', method=
    'GET', handle_http_exceptions=True, request_schema=entities.
    V1GetUserRoles, response_schema=entities.GetUserRolesResponse)
v1_get_userids_by_rolename = _api.make_client(path=
    '/v1/get-userids-by-rolename/', method='GET', handle_http_exceptions=
    True, request_schema=entities.V1GetUseridsByRolename, response_schema=
    entities.GetUserIdsByRoleNameResponse)
v1_get_users = _api.make_client(path='/v1/get-users/', method='POST',
    handle_http_exceptions=True, request_schema=entities.UserIdsRequest,
    response_schema=entities.GetUsersResponse)
v1_register_user_by_phone = _api.make_client(path=
    '/v1/register-user-by-phone/', method='POST', handle_http_exceptions=
    True, request_schema=entities.RegisterUserByPhoneRequest,
    response_schema=entities.RegisterUserByPhoneResponse)
v1_user_has_role = _api.make_client(path='/v1/user-has-role/', method='GET',
    handle_http_exceptions=True, request_schema=entities.V1UserHasRole,
    response_schema=bool)
v2_get_users_by_phone = _api.make_client(path='/v2/get-users-by-phone/',
    method='GET', handle_http_exceptions=True, request_schema=entities.
    V2GetUsersByPhone, response_schema=entities.GetUsersByPhoneResponseV2)
