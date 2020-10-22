from cian_entities import EntityMapper
from cian_entities.mappers import ValueMapper

from external_offers.entities import OfferStatusHistory


offer_status_history_mapper = EntityMapper(
    OfferStatusHistory,
    without_camelcase=True,
    mappers={
        'created_at': ValueMapper(),
    }
)
