from typing import Any

from jinja2 import Environment, PackageLoader
from simple_settings import settings

from external_offers.entities.parsed_offers import ParsedObjectModel
from external_offers.templates.filters import custom_filters


templates = Environment(
    loader=PackageLoader('external_offers'),
    autoescape=True
)
templates.filters.update(custom_filters)


def get_offers_list_html(offers: Any, client: Any) -> str:
    template = templates.get_template('offers_list.jinja2')
    return template.render(
        offers=offers,
        client=client,
        debug=settings.DEBUG
    )


def get_offer_card_html(parsed_object_model: ParsedObjectModel, info_message: str) -> str:
    template = templates.get_template('admin_debug.jinja2')
    return template.render(
        parsed_object_model=parsed_object_model,
        info_message=info_message,
        debug=settings.DEBUG
    )
