from datetime import datetime, timedelta

import pytz
from cian_core.runtime_settings import runtime_settings
from simple_settings import settings

from external_offers.entities.teams import Team
from external_offers.enums.operator_role import OperatorRole
from external_offers.enums.user_segment import UserSegment
from external_offers.helpers.region_names import REGION_NAMES
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import (
    Category,
    Status as PublicationStatus,
)
from external_offers.repositories.postgresql import (
    exists_offers_draft_by_client,
    exists_offers_in_progress_by_operator_and_offer_id,
    get_client_in_progress_by_operator,
    get_enriched_offers_in_progress_by_operator,
    get_offer_by_offer_id,
    get_parsed_offer_object_model_by_offer_id,
)
from external_offers.repositories.postgresql.clients import get_client_is_calltracking_by_client_id
from external_offers.repositories.postgresql.offers import get_offer_comment_by_offer_id
from external_offers.repositories.postgresql.operators import (
    get_enriched_operator_by_id,
    get_enriched_operators,
    get_enriched_teamleads,
    get_latest_operator_updating,
)
from external_offers.repositories.postgresql.teams import get_team_by_id, get_teams
from external_offers.services.accounts.client_accounts import get_client_accounts_by_phone_number_degradation_handler
from external_offers.services.operator_roles import get_operator_roles, get_or_create_operator, update_operators
from external_offers.services.possible_appointments import get_possible_appointments
from external_offers.templates import (
    get_offer_card_html,
    get_offers_list_html,
    get_operator_card_html,
    get_team_card_html,
    get_teams_page_html,
)
from external_offers.utils.teams import get_team_info
from external_offers.web.handlers.base import PublicHandler


class AdminOffersListPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        current_operator = await get_or_create_operator(
            operator_id=self.realty_user_id
        )

        client = await get_client_in_progress_by_operator(
            operator_id=self.realty_user_id
        )
        call_to_phone = ''
        if client and client.real_phone:
            call_to_phone = client.real_phone
        elif client and len(client.client_phones) > 0:
            call_to_phone = client.client_phones[0]
        client_is_calltracking = False
        client_comment = ''
        if client:
            client_is_calltracking = await get_client_is_calltracking_by_client_id(
                client_id=client.client_id
            )
            client_comment = client.comment or ''
            client_comment = client_comment.replace('\n', '; ')
        offers = await get_enriched_offers_in_progress_by_operator(
            operator_id=self.realty_user_id,
        )
        now = datetime.now()
        default_real_phone_hunted_at = now.replace(
            hour=runtime_settings.NEXT_CALL_HOUR,
            minute=runtime_settings.NEXT_CALL_MINUTES,
            second=runtime_settings.NEXT_CALL_SECONDS
        )
        next_call_day = now + timedelta(days=settings.NEXT_CALL_DAY)
        next_call_datetime = next_call_day.replace(
            hour=settings.NEXT_CALL_HOUR,
            minute=settings.NEXT_CALL_MINUTES,
            second=settings.NEXT_CALL_SECONDS
        )
        operator_roles = []
        if not runtime_settings.DEBUG:
            operator_roles = await get_operator_roles(operator_id=self.realty_user_id)
        is_commercial_moderator = OperatorRole.commercial_prepublication_moderator.value in operator_roles
        team_id = current_operator.team_id
        team = await get_team_by_id(team_id=team_id)
        team_info = get_team_info(team=team)
        operator_can_call_unhunted_ct = team_info.team_settings.get('enable_only_unhunted_ct', False)
        self.write(get_offers_list_html(
            client_is_calltracking=client_is_calltracking,
            offers=offers,
            client=client,
            client_comment=client_comment,
            call_to_phone=call_to_phone,
            default_next_call_datetime=next_call_datetime,
            operator_is_tester=self.realty_user_id in runtime_settings.TEST_OPERATOR_IDS,
            operator_id=self.realty_user_id,
            is_commercial_moderator=is_commercial_moderator,
            current_operator=current_operator,
            operator_can_call_unhunted_ct=operator_can_call_unhunted_ct,
            default_real_phone_hunted_at=default_real_phone_hunted_at,
            now=now,
        ))


class AdminOffersCardPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self, offer_id: str) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        current_operator = await get_or_create_operator(
            operator_id=self.realty_user_id
        )

        client = await get_client_in_progress_by_operator(
            operator_id=self.realty_user_id
        )
        if not client:
            self.write('???????????? ???? ????????????'.encode('utf-8'))
            return

        offer = await get_offer_by_offer_id(offer_id=offer_id)
        if not offer:
            self.write('???????????????????? ???? ??????????????'.encode('utf-8'))
            return

        exists = await exists_offers_in_progress_by_operator_and_offer_id(
            operator_id=self.realty_user_id,
            offer_id=offer_id
        )
        if not exists:
            self.write('???????????????????? ?? ???????????? ???? ??????????????'.encode('utf-8'))
            return

        offer_object_model = await get_parsed_offer_object_model_by_offer_id(
            offer_id=offer_id
        )

        offer_comment = await get_offer_comment_by_offer_id(offer_id)

        if not offer_object_model:
            self.write('???????????????????? ???? ???????????????? ?????????????????? ???? ??????????????'.encode('utf-8'))
            return

        client_accounts_result = await get_client_accounts_by_phone_number_degradation_handler(
            phone=client.client_phones[0]
        )

        appointments = await get_possible_appointments()
        exist_drafts = await exists_offers_draft_by_client(
            client_id=client.client_id
        )

        offer_is_draft = offer.publication_status == PublicationStatus.draft
        # ?????????????????? ?????? ???????????????????? ???????????? ???????????????????????? ???? ???????????????????????? ????????????????????????
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
            offer_comment=offer_comment,
            current_operator=current_operator,
        )

        self.write(offer_html)


class AdminTeamsPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        current_operator = await get_or_create_operator(
            operator_id=self.realty_user_id
        )

        last_updating = await get_latest_operator_updating()
        if (not last_updating) or (last_updating < datetime.now(tz=pytz.UTC) - timedelta(days=1)):
            await update_operators()
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
        teams = await get_teams()
        self.write(get_operator_card_html(
            current_operator=current_operator,
            operator=operator,
            teams=teams,
        ))


def _get_commercial_categories() -> list[str]:
    return [
        Category.office_sale.value,
        Category.free_appointment_object_sale.value,
        Category.shopping_area_sale.value,
        Category.warehouse_sale.value,
        Category.industry_sale.value,
        Category.building_sale.value,
        Category.business_sale.value,
        Category.commercial_land_sale.value,
        Category.office_rent.value,
        Category.free_appointment_object_rent.value,
        Category.shopping_area_rent.value,
        Category.warehouse_rent.value,
        Category.industry_rent.value,
        Category.building_rent.value,
        Category.business_rent.value,
        Category.commercial_land_rent.value,
    ]


def _get_categories() -> list[str]:
    return [category.value for category in Category]


def _get_segments() -> list[str]:
    return [segment.value for segment in UserSegment]


def _get_regions() -> dict[str, str]:
    return REGION_NAMES


def _get_subsegments() -> list[str]:
    return [
        'commercial',
        'a > 1000',
        'a 500-1000',
        'b 300-500',
        'b 30-300',
        'c >= 60',
        'c 50-60',
        'c 40-50',
        'c 30-40',
        'c 20-30',
        'c 10-20',
        'c 5-10',
        'c 3-5',
        'c < 3',
        'd',
    ]


def _get_team_settings(team: Team):
    return team.get_settings()


class AdminTeamCardPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    async def get(self, team_id: str) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        current_operator = await get_or_create_operator(
            operator_id=self.realty_user_id
        )


        team = await get_team_by_id(int(team_id))
        teamleads = await get_enriched_teamleads()
        teams = await get_teams()
        categories = _get_categories()
        commercial_categories = _get_commercial_categories()
        segments = _get_segments()
        regions = _get_regions()
        subsegments = _get_subsegments()
        team_settings = _get_team_settings(team) if team else {}
        self.write(get_team_card_html(
            current_operator=current_operator,
            team=team,
            team_settings=team_settings,
            teamleads=teamleads,
            teams=teams,
            categories=categories,
            commercial_categories=commercial_categories,
            regions=regions,
            segments=segments,
            subsegments=subsegments,
            operator_is_tester=self.realty_user_id in runtime_settings.TEST_OPERATOR_IDS,
        ))
