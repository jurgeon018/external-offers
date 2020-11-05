from cian_core.web import base_urls
from cian_web import get_handler
from tornado.web import url

from external_offers import entities
from external_offers.services.save_offer import save_offer_public
from external_offers.web import handlers
from external_offers.web.handlers.base import PublicHandler


urlpatterns = base_urls.urlpatterns + [
    # admin
    url('/admin/offers-list/$', handlers.AdminOffersListPageHandler),
    url('/admin/offer-card/$', handlers.AdminOffersCardPageHandler),
    url('/api/admin/v1/update-offers-list/$', handlers.AdminUpdateOffersListPageHandler),
    url('/api/admin/v1/decline-client/$', handlers.AdminDeclineClientHandler),
    url('/api/admin/v1/call-missed-client/$', handlers.AdminCallMissedClientHandler),
    url('/api/admin/v1/save-offer/$', get_handler(
        service=save_offer_public,
        method='POST',
        request_schema=entities.SaveOfferRequest,
        response_schema=entities.SaveOfferResponse,
        base_handler_cls=PublicHandler,
    )),
]
