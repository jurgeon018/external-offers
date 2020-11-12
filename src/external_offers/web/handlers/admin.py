import json

from simple_settings import settings

from external_offers.repositories.postgresql import (
    assign_waiting_client_to_operator,
    exists_offers_in_progress_by_client,
    exists_offers_in_progress_by_operator,
    exists_offers_in_progress_by_operator_and_offer_id,
    get_client_by_operator,
    get_client_id_by_offer_id,
    get_offers_in_progress_by_operator,
    get_parsed_offer_object_model_by_offer_id,
    set_client_to_call_missed_status,
    set_client_to_decline_status,
    set_client_to_waiting_status,
    set_offer_cancelled_by_offer_id,
    set_offers_call_missed_by_client,
    set_offers_declined_by_client,
    set_waiting_offers_in_progress_by_client,
)
from external_offers.templates import get_offer_card_html, get_offers_list_html
from external_offers.web.handlers.base import PublicHandler


class AdminOffersListPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
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
        client_id = params['client_id']

        await set_client_to_decline_status(client_id)
        await set_offers_declined_by_client(client_id)

        self.write(json.dumps({
                'success': True,
                'errors': [],
        }))


class AdminDeleteOfferClientHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def post(self) -> None:
        self.set_header('Content-Type', 'application/json')
        params = json.loads(self.request.body)
        offer_id = params['offer_id']
        client_id = params['client_id']

        await set_offer_cancelled_by_offer_id(offer_id)
        exists = await exists_offers_in_progress_by_client(client_id)

        if not exists:
            await set_client_to_waiting_status(client_id)

        self.write(json.dumps({
                'success': True,
                'errors': [],
        }))


class AdminCallMissedClientHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def post(self) -> None:
        self.set_header('Content-Type', 'application/json')
        params = json.loads(self.request.body)
        client_id = params['client_id']

        await set_client_to_call_missed_status(client_id)
        await set_offers_call_missed_by_client(client_id)

        self.write(json.dumps({
                'success': True,
                'errors': [],
        }))


class AdminOffersCardPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self, offer_id: str) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        exists = await exists_offers_in_progress_by_operator_and_offer_id(
            operator_id=self.realty_user_id,
            offer_id=offer_id
        )
        if not exists:
            self.write('Объявление в работе не найдено'.encode('utf-8'))
            return

        offer_object_model = await get_parsed_offer_object_model_by_offer_id(
            offer_id=offer_id
        )

        client_id = await get_client_id_by_offer_id(
            offer_id=offer_id
        )

        if not offer_object_model:
            self.write('Объявление из внешнего источника не найдено'.encode('utf-8'))
            return

        offer_html = get_offer_card_html(
            parsed_object_model=offer_object_model,
            info_message=settings.SAVE_OFFER_MSG,
            offer_id=offer_id,
            client_id=client_id,
        )

        self.write(offer_html)
