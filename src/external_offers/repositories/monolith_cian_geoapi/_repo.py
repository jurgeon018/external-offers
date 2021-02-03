# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-geoapi`

cian-codegen version: 1.7.1

"""
from cian_http.api_client import Api

from . import entities


_api = Api(microservice_name='monolith-cian-geoapi')
v2_geocode = _api.make_client(
    path='/v2/geocode/',
    method='POST',
    handle_http_exceptions=True,
    request_schema=entities.GeoCodedRequest,
    response_schema=entities.GeoCodedResponse,
)