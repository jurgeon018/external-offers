from datetime import datetime, timedelta

from cian_core.runtime_settings import runtime_settings
from simple_settings import settings

from external_offers.repositories.postgresql import (
    exists_offers_draft_by_client,
    exists_offers_in_progress_by_operator_and_offer_id,
    get_client_in_progress_by_operator,
    get_enriched_offers_in_progress_by_operator,
    get_parsed_offer_object_model_by_offer_id,
)
from external_offers.services.accounts.client_accounts import get_client_accounts_by_phone_number_degradation_handler
from external_offers.templates import get_offer_card_html, get_offers_list_html
from external_offers.web.handlers.base import PublicHandler


class AdminOffersListPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        client = await get_client_in_progress_by_operator(
            operator_id=self.realty_user_id
        )
        offers = await get_enriched_offers_in_progress_by_operator(
            operator_id=self.realty_user_id
        )
        now = datetime.now()
        next_call_day = now + timedelta(days=settings.NEXT_CALL_DAY)
        next_call_datetime = next_call_day.replace(
            hour=settings.NEXT_CALL_HOUR,
            minute=settings.NEXT_CALL_MINUTES,
            second=settings.NEXT_CALL_SECONDS
        )

        self.write(get_offers_list_html(
            offers=offers,
            client=client,
            default_next_call_datetime=next_call_datetime,
            operator_is_tester=self.realty_user_id in runtime_settings.TEST_OPERATOR_IDS,
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

        client = await get_client_in_progress_by_operator(
            operator_id=self.realty_user_id
        )

        if not offer_object_model:
            self.write('Объявление из внешнего источника не найдено'.encode('utf-8'))
            return

        client_accounts_result = await get_client_accounts_by_phone_number_degradation_handler(
            phone=client.client_phones[0]
        )

        exist_drafts = await exists_offers_draft_by_client(
            client_id=client.client_id
        )
        offer_html = get_offer_card_html(
            parsed_object_model=offer_object_model,
            info_message=settings.SAVE_OFFER_MSG,
            offer_id=offer_id,
            client=client,
            client_accounts=client_accounts_result.value,
            exist_drafts=exist_drafts
        )

        self.write(offer_html)
