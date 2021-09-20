from cian_entities import EntityMapper

from external_offers.entities import Operator, Team, EnrichedOperator


teams_mapper = EntityMapper(
    Team,
    without_camelcase=True,
)
operators_mapper = EntityMapper(
    Operator,
    without_camelcase=True,
)
enriched_operators_mapper = EntityMapper(
    EnrichedOperator,
    without_camelcase=True,
)
