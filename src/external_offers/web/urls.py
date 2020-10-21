from cian_core.web import base_urls
from tornado.web import url

from external_offers.web.handlers import AdminExternalOffersPageHandler


urlpatterns = base_urls.urlpatterns + [
    url(
        '/admin/external_offers/$', AdminExternalOffersPageHandler
    ),
]
