# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.17.0

"""
from typing import List

from cian_http.api_client import Api

from . import entities


_api = Api(microservice_name='monolith-cian-announcementapi')
announcement_references_commercial_get_possible_appointments = _api.make_client(
    path='/announcement-references/commercial/get-possible-appointments/',
    method='GET',
    handle_http_exceptions=True,
    response_schema=List[entities.CommercialPossibleAppointmentModel],
)
v1_geo_geocode = _api.make_client(
    path='/v1/geo/geocode/',
    method='GET',
    handle_http_exceptions=True,
    request_schema=entities.V1GeoGeocode,
    response_schema=entities.GeoCodeAnnouncementResponse,
)
v2_announcements_draft = _api.make_client(
    path='/v2/announcements/draft/',
    method='POST',
    handle_http_exceptions=True,
    request_schema=entities.PublicationModel,
    response_schema=entities.AddDraftResult,
)
