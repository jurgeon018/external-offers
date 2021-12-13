from cian_entities import EntityMapper

from external_offers.entities.account_priorities import AccountPriority


account_priority_mapper = EntityMapper(
    AccountPriority,
    without_camelcase=True,
)
