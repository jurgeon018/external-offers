from cian_core.web import base_urls
from tornado.web import url

from external_offers.web.handlers import AdminOffersListPageHandler, AdminUpdateOffersListPageHandler


urlpatterns = base_urls.urlpatterns + [
    url(
        '/admin/offers-list/$', AdminOffersListPageHandler
    ),
    url(
        '/admin/update-offers-list/$', AdminUpdateOffersListPageHandler
    ),
]
