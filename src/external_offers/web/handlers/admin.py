from simple_settings import settings

from external_offers.repositories.postgresql import (
    exists_offers_in_progress_by_operator_and_offer_id,
    get_client_by_operator,
    get_client_id_by_offer_id,
    get_enriched_offers_in_progress_by_operator,
    get_offers_in_progress_by_operator,
    get_parsed_offer_object_model_by_offer_id,
)
from external_offers.templates import get_offer_card_html, get_offers_list_html
from external_offers.web.handlers.base import PublicHandler


class AdminOffersListPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        client = await get_client_by_operator(self.realty_user_id)
        offers = await get_enriched_offers_in_progress_by_operator(self.realty_user_id)

        self.write(get_offers_list_html(
            offers=offers,
            client=client
        ))


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
