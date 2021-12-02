from cian_entities import EntityMapper
from cian_entities.mappers import ValueMapper

from external_offers.entities.parsed_offers import ParsedOffer, ParsedOfferForCreation, ParsedOfferMessage


parsed_offer_message_mapper = EntityMapper(
    ParsedOfferMessage,
    without_camelcase=True,
    mappers={
        'timestamp': ValueMapper(),
    }
)

parsed_offer_mapper = EntityMapper(
    ParsedOffer,
    without_camelcase=True,
    mappers={
        'timestamp': ValueMapper(),
        'created_at': ValueMapper(),
        'updated_at': ValueMapper(),
    }
)

parsed_offer_for_creation_mapper = EntityMapper(
    ParsedOfferForCreation,
    without_camelcase=True,
    mappers={
        'timestamp': ValueMapper(),
    }
)
