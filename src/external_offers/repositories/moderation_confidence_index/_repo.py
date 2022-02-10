# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client moderation-confidence-index`

cian-codegen version: 1.17.0

"""
from cian_http.api_client import Api

from . import entities


_api = Api(microservice_name='moderation-confidence-index')
api_call_component_v1_get_operator_calls = _api.make_client(
    path='/api/call-component/v1/get-operator-calls',
    method='POST',
    handle_http_exceptions=True,
    request_schema=entities.GetOperatorCallsFilter,
    response_schema=entities.GetOperatorCallsResponseModel,
)
