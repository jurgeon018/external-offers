from cian_entities.mappers import EntityMapper, ValueMapper

from external_offers.entities import EnrichedOperator, Operator, Team


teams_mapper = EntityMapper(
    Team,
    without_camelcase=True,
    mappers={
        'settings': ValueMapper(),
    }
)
operators_mapper = EntityMapper(
    Operator,
    without_camelcase=True,
    mappers={
        'created_at': ValueMapper(),
        'updated_at': ValueMapper(),
    }
)
enriched_operators_mapper = EntityMapper(
    EnrichedOperator,
    without_camelcase=True,
    mappers={
        'settings': ValueMapper(),
        'created_at': ValueMapper(),
        'updated_at': ValueMapper(),
    }
)
