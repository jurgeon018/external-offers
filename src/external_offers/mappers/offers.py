from cian_entities import EntityMapper
from cian_entities.mappers import ValueMapper

from external_offers.entities import EnrichedOffer, Offer
from external_offers.entities.offers import OfferForPrioritization


offer_mapper = EntityMapper(
    Offer,
    without_camelcase=True,
    mappers={
        'created_at': ValueMapper(),
        'parsed_created_at': ValueMapper(),
        'started_at': ValueMapper(),
        'synced_at': ValueMapper()
    }
)

enriched_offer_mapper = EntityMapper(
    EnrichedOffer,
    without_camelcase=True,
    mappers={
        'created_at': ValueMapper(),
        'started_at': ValueMapper(),
        'synced_at': ValueMapper()
    }
)

offer_for_prioritization_mapper = EntityMapper(
    OfferForPrioritization,
    without_camelcase=True,
)
