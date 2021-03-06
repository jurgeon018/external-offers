from datetime import datetime
from typing import Any, List, Optional

from cian_core.runtime_settings import runtime_settings
from jinja2 import Environment, PackageLoader

from external_offers.entities import Client, ClientAccountInfo, EnrichedOffer, EnrichedOperator, Team
from external_offers.entities.parsed_offers import ParsedObjectModel
from external_offers.repositories.monolith_cian_announcementapi.entities import CommercialPossibleAppointmentModel
from external_offers.templates.filters import custom_filters


templates = Environment(
    loader=PackageLoader('external_offers'),
    autoescape=True
)
templates.filters.update(custom_filters)


def get_html(template_name: str, **kwargs) -> str:
    template = templates.get_template(template_name)
    return template.render(
        debug=runtime_settings.DEBUG,
        **kwargs,
    )


def get_offers_list_html(
    *,
    client_is_calltracking: bool,
    offers: List[EnrichedOffer],
    client: Optional[Client],
    client_comment: Optional[str] = None,
    call_to_phone: str,
    default_next_call_datetime: datetime,
    operator_is_tester: bool,
    operator_id: int,
    is_commercial_moderator: bool,
    current_operator: EnrichedOperator,
    operator_can_call_unhunted_ct: bool,
    default_real_phone_hunted_at: datetime,
    now: datetime,
) -> str:
    dt_format = '%Y-%m-%dT%H:%M:%S'
    template = templates.get_template('offers_list.jinja2')
    return template.render(
        client_is_calltracking=client_is_calltracking,
        offers=offers,
        client=client,
        client_comment=client_comment,
        call_to_phone=call_to_phone,
        next_call_datetime=default_next_call_datetime.strftime(dt_format),
        debug=runtime_settings.DEBUG,
        operator_is_tester=operator_is_tester,
        operator_id=operator_id,
        is_commercial_moderator=is_commercial_moderator,
        current_operator=current_operator,
        operator_can_call_unhunted_ct=operator_can_call_unhunted_ct,
        default_real_phone_hunted_at=default_real_phone_hunted_at.strftime(dt_format),
        now=now.strftime(dt_format),
    )


def get_offer_card_html(
    *,
    parsed_object_model: ParsedObjectModel,
    info_message: str,
    offer_id: str,
    client: Client,
    client_accounts: List[ClientAccountInfo],
    exist_drafts: bool,
    offer_is_draft: bool = False,
    appointments: List[CommercialPossibleAppointmentModel],
    is_ready_business_enabled: bool = False,
    offer_comment: Optional[str] = None,
    current_operator: EnrichedOperator,
) -> str:
    template = templates.get_template('offer_card.jinja2')
    # template = templates.get_template('admin_debug.jinja2')
    return template.render(
        parsed_object_model=parsed_object_model,
        info_message=info_message,
        debug=runtime_settings.DEBUG,
        offer_id=offer_id,
        appointments=appointments,
        client=client,
        client_accounts=client_accounts,
        exist_drafts=exist_drafts,
        offer_is_draft=offer_is_draft,
        is_ready_business_enabled=1 if is_ready_business_enabled is True else 0,
        offer_comment=offer_comment,
        current_operator=current_operator,
    )


def get_teams_page_html(
    current_operator: EnrichedOperator,
    operators: list[EnrichedOperator],
    teams: list[Team],
) -> str:
    template = templates.get_template('teams.jinja2')
    return template.render(
        debug=runtime_settings.DEBUG,
        current_operator=current_operator,
        operators=operators,
        teams=teams,
    )


def get_team_card_html(
    current_operator: EnrichedOperator,
    team: Optional[Team],
    team_settings: dict[str, Any],
    teamleads: list[EnrichedOperator],
    teams: list[Team],
    categories: list[str],
    commercial_categories: list[str],
    regions: dict[str, str],
    segments: list[str],
    subsegments: list[str],
    operator_is_tester: bool,
) -> str:
    template = templates.get_template('team_card.jinja2')
    return template.render(
        debug=runtime_settings.DEBUG,
        current_operator=current_operator,
        team=team,
        team_settings=team_settings,
        teamleads=teamleads,
        teams=teams,
        commercial_categories=commercial_categories,
        categories=categories,
        regions=regions,
        segments=segments,
        subsegments=subsegments,
        operator_is_tester=operator_is_tester,
    )


def get_operator_card_html(
    current_operator: EnrichedOperator,
    operator: Optional[EnrichedOperator],
    teams: list[Team],
) -> str:
    template = templates.get_template('operator_card.jinja2')
    return template.render(
        debug=runtime_settings.DEBUG,
        current_operator=current_operator,
        operator=operator,
        teams=teams,
    )
