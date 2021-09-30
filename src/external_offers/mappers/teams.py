from cian_entities import EntityMapper
from cian_entities.mappers import (
    StrKeyDictMapper,
    ValueMapper,
    EntityMapper,
    
)
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
)
enriched_operators_mapper = EntityMapper(
    EnrichedOperator,
    without_camelcase=True,
    mappers={
        'settings': ValueMapper(),
    }
)
