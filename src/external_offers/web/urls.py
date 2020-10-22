from cian_core.web import base_urls
from tornado.web import url

from external_offers.web.handlers import AdminOffersListPageHandler


urlpatterns = base_urls.urlpatterns + [
    url(
        '/admin/offers-list/$', AdminOffersListPageHandler
    ),
]
