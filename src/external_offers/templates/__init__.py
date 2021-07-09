from datetime import datetime
from typing import Any, List, Optional

from jinja2 import Environment, PackageLoader
from simple_settings import settings

from external_offers.entities import Client, ClientAccountInfo, EnrichedOffer
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
    default_next_call_datetime: datetime
) -> str:
    template = templates.get_template('offers_list.jinja2')
    return template.render(
        offers=offers,
        client=client,
        next_call_datetime=default_next_call_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
        debug=settings.DEBUG
    )


def get_offer_card_html(
    *,
    parsed_object_model: ParsedObjectModel,
    info_message: str,
    offer_id: str,
    client: Client,
    client_accounts: List[ClientAccountInfo],
    exist_drafts: bool,
) -> str:
    # template = templates.get_template('offer_card.jinja2')
    template = templates.get_template('admin_debug.jinja2')
    
    return template.render(
        parsed_object_model=parsed_object_model,
        info_message=info_message,
        debug=settings.DEBUG,
        offer_id=offer_id,
        client=client,
        client_accounts=client_accounts,
        exist_drafts=exist_drafts
    )
