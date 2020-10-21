from typing import Any, Dict

from jinja2 import Environment, PackageLoader

from external_offers.templates.filters import custom_filters


templates = Environment(loader=PackageLoader('external_offers'))
templates.filters.update(custom_filters)


def get_external_offers_html(offers: Any, client: Any) -> str:
    template = templates.get_template('external_offers.jinja2')
    return template.render(
        offers=offers,
        client=client
    )
