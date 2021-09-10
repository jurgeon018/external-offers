from datetime import datetime
from typing import List, Optional

from cian_core.runtime_settings import runtime_settings
from jinja2 import Environment, PackageLoader

from external_offers.entities import Client, ClientAccountInfo, EnrichedOffer, Operator, Team
from external_offers.entities.parsed_offers import ParsedObjectModel
from external_offers.templates.filters import custom_filters


templates = Environment(
    loader=PackageLoader('external_offers'),
    autoescape=True
)
templates.filters.update(custom_filters)


def get_offers_list_html(
    *,
    offers: List[EnrichedOffer],
    client: Optional[Client],
    default_next_call_datetime: datetime,
    operator_is_tester: bool,
) -> str:
    template = templates.get_template('offers_list.jinja2')
    return template.render(
        offers=offers,
        client=client,
        next_call_datetime=default_next_call_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
        debug=runtime_settings.DEBUG,
        operator_is_tester=operator_is_tester,
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
) -> str:
    template = templates.get_template('offer_card.jinja2')
    # template = templates.get_template('admin_debug.jinja2')

    return template.render(
        parsed_object_model=parsed_object_model,
        info_message=info_message,
        debug=runtime_settings.DEBUG,
        offer_id=offer_id,
        client=client,
        client_accounts=client_accounts,
        exist_drafts=exist_drafts,
        offer_is_draft=offer_is_draft,
    )


def get_teams_page_html(
    current_operator: Operator,
    operators: list[Operator],
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
    current_operator: Operator,
    team: Team,
    operators: list[Operator],
    teams: list[Team],
) -> str:
    template = templates.get_template('team_card.jinja2')
    return template.render(
        debug=runtime_settings.DEBUG,
        current_operator=current_operator,
        team=team,
        operators=operators,
        teams=teams,
    )


def get_operator_card_html(
    current_operator: Operator,
    operator: Operator,
    operators: list[Operator],
    teams: list[Team],
) -> str:
    template = templates.get_template('operator_card.jinja2')
    return template.render(
        debug=runtime_settings.DEBUG,
        current_operator=current_operator,
        operator=operator,
        operators=operators,
        teams=teams,
    )
