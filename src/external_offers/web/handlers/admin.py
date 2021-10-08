from datetime import datetime, timedelta

import pytz
from cian_core.runtime_settings import runtime_settings
from simple_settings import settings

from external_offers.enums.operator_role import OperatorRole
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import Status as PublicationStatus
from external_offers.repositories.postgresql import (
    exists_offers_draft_by_client,
    exists_offers_in_progress_by_operator_and_offer_id,
    get_client_in_progress_by_operator,
    get_enriched_offers_in_progress_by_operator,
    get_offer_by_offer_id,
    get_parsed_offer_object_model_by_offer_id,
)
from external_offers.repositories.postgresql.operators import (
    get_enriched_operator_by_id,
    get_enriched_operators,
    get_latest_operator_updating,
)
from external_offers.repositories.postgresql.teams import get_team_by_id, get_teams
from external_offers.services.accounts.client_accounts import get_client_accounts_by_phone_number_degradation_handler
from external_offers.services.operator_roles import (
    create_operators_from_cian,
    get_operator_roles,
    get_or_create_operator,
)
from external_offers.services.possible_appointments import get_possible_appointments
from external_offers.templates import (
    get_offer_card_html,
    get_offers_list_html,
    get_operator_card_html,
    get_team_card_html,
    get_teams_page_html,
)
from external_offers.web.handlers.base import PublicHandler


class AdminOffersListPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        client = await get_client_in_progress_by_operator(
            operator_id=self.realty_user_id
        )
        unactivated = False
        if client:
            unactivated = client.unactivated
        offers = await get_enriched_offers_in_progress_by_operator(
            operator_id=self.realty_user_id,
            unactivated=unactivated,
        )
        now = datetime.now()
        next_call_day = now + timedelta(days=settings.NEXT_CALL_DAY)
        next_call_datetime = next_call_day.replace(
            hour=settings.NEXT_CALL_HOUR,
            minute=settings.NEXT_CALL_MINUTES,
            second=settings.NEXT_CALL_SECONDS
        )
        operator_roles = await get_operator_roles(operator_id=self.realty_user_id)
        is_commercial_moderator = OperatorRole.commercial_prepublication_moderator.value in operator_roles

        self.write(get_offers_list_html(
            offers=offers,
            client=client,
            default_next_call_datetime=next_call_datetime,
            operator_is_tester=self.realty_user_id in runtime_settings.TEST_OPERATOR_IDS,
            is_commercial_moderator=is_commercial_moderator,
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

        appointments = await get_possible_appointments()
        exist_drafts = await exists_offers_draft_by_client(
            client_id=client.client_id
        )
        offer = await get_offer_by_offer_id(offer_id=offer_id)
        offer_is_draft = offer.publication_status == PublicationStatus.draft
        # Настройка для корректной работы обновленного ГБ коммерческой недвижимости
        # https://conf.cian.tech/pages/viewpage.action?pageId=1305332955
        is_ready_business_enabled = runtime_settings.get('EXTERNAL_OFFERS_READY_BUSINESS_ENABLED', False)
        offer_html = get_offer_card_html(
            parsed_object_model=offer_object_model,
            info_message=settings.SAVE_OFFER_MSG,
            offer_id=offer_id,
            client=client,
            client_accounts=client_accounts_result.value,
            exist_drafts=exist_drafts,
            offer_is_draft=offer_is_draft,
            appointments=appointments,
            is_ready_business_enabled=is_ready_business_enabled,
        )

        self.write(offer_html)


class AdminTeamsPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        last_updating = await get_latest_operator_updating()
        if not last_updating:
            await create_operators_from_cian()
        elif last_updating < datetime.now(tz=pytz.UTC) - timedelta(days=1):
            await create_operators_from_cian()
        current_operator = await get_or_create_operator(
            operator_id=self.realty_user_id
        )
        operators = await get_enriched_operators()
        teams = await get_teams()
        self.write(get_teams_page_html(
            current_operator=current_operator,
            operators=operators,
            teams=teams,
        ))


class AdminOperatorCardPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self, operator_id: str) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        current_operator = await get_or_create_operator(
            operator_id=self.realty_user_id
        )
        operator = await get_enriched_operator_by_id(operator_id)
        operators = await get_enriched_operators()
        teams = await get_teams()
        self.write(get_operator_card_html(
            current_operator=current_operator,
            operator=operator,
            operators=operators,
            teams=teams,
        ))


class AdminTeamCardPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self, team_id: str) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        current_operator = await get_or_create_operator(
            operator_id=self.realty_user_id
        )
        team = await get_team_by_id(int(team_id))
        operators = await get_enriched_operators()
        teams = await get_teams()
        self.write(get_team_card_html(
            current_operator=current_operator,
            team=team,
            operators=operators,
            teams=teams,
        ))
