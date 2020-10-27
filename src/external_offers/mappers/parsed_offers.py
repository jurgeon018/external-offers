from cian_entities import EntityMapper
from cian_entities.mappers import ValueMapper

from external_offers.entities.parsed_offers import ParsedOffer


parsed_offer_mapper = EntityMapper(
    ParsedOffer,
    without_camelcase=True,
    mappers={
        'timestamp': ValueMapper(),
    }
)
