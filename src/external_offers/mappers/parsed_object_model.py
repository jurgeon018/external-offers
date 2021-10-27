from cian_entities import EntityMapper

from external_offers.entities.parsed_offers import ParsedObjectModel


parsed_object_model_mapper = EntityMapper(
    ParsedObjectModel,
    without_camelcase=True,
)
