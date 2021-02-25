from cian_core.web import base_urls
from cian_web import get_handler
from tornado.web import url

from external_offers import entities
from external_offers.services import admin
from external_offers.services.save_offer import save_offer_public
from external_offers.services.update_client_phone import update_client_phone_public
from external_offers.web import handlers
from external_offers.web.handlers.base import PublicHandler


urlpatterns = base_urls.urlpatterns + [
    # admin
    url('/admin/offers-list/$', handlers.AdminOffersListPageHandler),
    url(r'/admin/offer-card/(?P<offer_id>[a-zA-Z0-9-]+)/$', handlers.AdminOffersCardPageHandler),

    # admin actions
    url('/api/admin/v1/update-offers-list/$', get_handler(
        service=admin.update_offers_list,
        method='POST',
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/decline-client/$', get_handler(
        service=admin.set_decline_status_for_client,
        method='POST',
        request_schema=entities.AdminDeclineClientRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/delete-offer/$', get_handler(
        service=admin.delete_offer,
        method='POST',
        request_schema=entities.AdminDeleteOfferRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/call-missed-client/$', get_handler(
        service=admin.set_call_missed_status_for_client,
        method='POST',
        request_schema=entities.AdminCallMissedClientRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/call-later-client/$', get_handler(
        service=admin.set_call_later_status_for_client,
        method='POST',
        request_schema=entities.AdminCallMissedClientRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/save-offer/$', get_handler(
        service=save_offer_public,
        method='POST',
        request_schema=entities.SaveOfferRequest,
        response_schema=entities.SaveOfferResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-client-phone/$', get_handler(
        service=update_client_phone_public,
        method='POST',
        request_schema=entities.UpdateClientPhoneRequest,
        response_schema=entities.UpdateClientPhoneResponse,
        base_handler_cls=PublicHandler,
    )),
]
