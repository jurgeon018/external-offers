from cian_entities import EntityMapper

from external_offers.entities.client_account_statuses import ClientAccountStatus


client_account_status_mapper = EntityMapper(
    ClientAccountStatus,
    without_camelcase=True,
)
