from cian_schemas import EntitySchema

from external_offers.entities.parsed_offers import ParsedOffer


class ParsedOfferSchema(EntitySchema):
    class Meta:
        entity = ParsedOffer
