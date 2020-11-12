# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-service`

cian-codegen version: 1.7.1

"""
from cian_http.api_client import Api

from . import entities


_api = Api(microservice_name='monolith-cian-service')
api_promocodes_create_promocode_group = _api.make_client(
    path='/api/promocodes/create-promocode-group',
    method='POST',
    handle_http_exceptions=True,
    request_schema=entities.PromoCodeGroupDetailModel,
    response_schema=entities.CreatePromocodeGroupResponse,
)