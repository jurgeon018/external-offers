import json

from external_offers.repositories.postgresql import (
    assign_waiting_client_to_operator,
    exists_offers_in_progress_by_operator,
    get_client_by_operator,
    get_offers_in_progress_by_operator,
    set_waiting_offers_in_progress_by_client,
)
from external_offers.templates import get_offers_list_html
from external_offers.web.handlers.base import PublicHandler


class AdminOffersListPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html')

        client = await get_client_by_operator(self.realty_user_id)
        offers = await get_offers_in_progress_by_operator(self.realty_user_id)

        self.write(get_offers_list_html(
                offers=offers,
                client=client
            )
        )


class AdminUpdateOffersListPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def post(self) -> None:
        self.set_header('Content-Type', 'application/json')

        exists = await exists_offers_in_progress_by_operator(self.realty_user_id)

        if exists:
            self.write(json.dumps({
                'success': False,
                'errors': [{
                    'message': 'Есть объявления в работе, завершите их',
                    'code': 'offersInProgressExist'
                }],
            }))
            return
        client_id = await assign_waiting_client_to_operator(self.realty_user_id)
        await set_waiting_offers_in_progress_by_client(client_id)

        self.write(json.dumps({
                'success': True,
                'errors': [],
            }))
