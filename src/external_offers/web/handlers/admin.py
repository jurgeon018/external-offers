from external_offers.repositories.postgresql import get_client_by_operator, get_offers_in_progress_by_operator
from external_offers.templates import get_external_offers_html
from external_offers.web.handlers.base import PublicHandler


class AdminOffersListPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        client = await get_client_by_operator(self.realty_user_id)
        offers = await get_offers_in_progress_by_operator(self.realty_user_id)

        self.set_header('content-type', 'text/html')
        self.write(get_external_offers_html(
                offers=offers,
                client=client
            )
        )
