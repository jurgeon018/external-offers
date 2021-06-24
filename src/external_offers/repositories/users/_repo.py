# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client users`

cian-codegen version: 1.9.0

"""
from cian_core.runtime_settings import runtime_settings
from cian_http.api_client import Api

from . import entities


_api = Api(microservice_name='users')
v1_register_user_by_phone = _api.make_client(
    path='/v1/register-user-by-phone/',
    method='POST',
    handle_http_exceptions=True,
    request_schema=entities.RegisterUserByPhoneRequest,
    response_schema=entities.RegisterUserByPhoneResponse,
    default_timeout=runtime_settings.V1_REGISTER_USER_BY_PHONE_TIMEOUT,
)
v2_get_users_by_phone = _api.make_client(
    path='/v2/get-users-by-phone/',
    method='GET',
    handle_http_exceptions=True,
    request_schema=entities.V2GetUsersByPhone,
    response_schema=entities.GetUsersByPhoneResponseV2,
    default_timeout=runtime_settings.V2_GET_USERS_BY_PHONE_TIMEOUT,
)
