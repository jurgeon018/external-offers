from cian_core.web import base_urls
from cian_web import get_handler
from external_offers.web.handlers.base import PublicHandler
from tornado.web import url

from external_offers import entities
from external_offers.services.save_offer import save_offer_public
from external_offers.web import handlers


urlpatterns = base_urls.urlpatterns + [
    # admin
    url('/admin/offers-list/$', handlers.AdminOffersListPageHandler),
    url('/admin/update-offers-list/$', handlers.AdminUpdateOffersListPageHandler),

    url('/admin/offer-card/$', handlers.AdminOffersCardPageHandler),
    url('/admin/offer-card/debug/$', handlers.AdminOffersCardPageHandlerDebug),  # TODO: delete

    url('/api/admin/v1/save-offer/$', get_handler(
        service=save_offer_public,
        method='POST',
        request_schema=entities.SaveOfferRequest,
        response_schema=entities.SaveOfferResponse,
        base_handler_cls=PublicHandler,
    )),
]
