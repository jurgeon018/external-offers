from cian_entities import EntityMapper
from cian_entities.mappers import ValueMapper

from external_offers.entities import Offer


offer_mapper = EntityMapper(
    Offer,
    without_camelcase=True,
    mappers={
        'created_at': ValueMapper(),
        'started_at': ValueMapper(),
        'synced_at': ValueMapper()
    }
)
