from cian_entities import EntityMapper

from external_offers.entities import Operator, Role, Team


teams_mapper = EntityMapper(
    Team,
    without_camelcase=True,
)
operators_mapper = EntityMapper(
    Operator,
    without_camelcase=True,
)
roles_mapper = EntityMapper(
    Role,
    without_camelcase=True,
)
