import json

from simple_settings import settings

from external_offers.repositories.postgresql import (
    assign_waiting_client_to_operator,
    exists_offers_in_progress_by_operator,
    get_client_by_operator,
    get_offers_in_progress_by_operator,
    set_client_to_decline_status,
    set_offers_declined_by_client,
    set_waiting_offers_in_progress_by_client,
)
from external_offers.services.parsed_offers import get_parsed_offer
from external_offers.templates import get_offer_card_html, get_offer_card_html_debug, get_offers_list_html
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
        ))


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


class AdminDeclineClientHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def post(self) -> None:
        self.set_header('Content-Type', 'application/json')
        params = json.loads(self.request.body)

        await set_client_to_decline_status(params['client_id'])
        await set_offers_declined_by_client(params['client_id'])
        self.write(json.dumps({
                'success': True,
                'errors': [],
        }))
            'success': True,
            'errors': [],
        }))


class AdminOffersCardPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html')

        offer = await get_parsed_offer(parsed_offer_id='123')
        offer_html = get_offer_card_html(
            parsed_object_model=offer,
            info_message=settings.SAVE_OFFER_MSG
        )
        self.write(offer_html)


class AdminOffersCardPageHandlerDebug(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html')
        offer = await get_parsed_offer(parsed_offer_id='123')
        offer_html = get_offer_card_html_debug(
            parsed_object_model=offer,
            info_message=settings.SAVE_OFFER_MSG
        )
        self.write(offer_html)
