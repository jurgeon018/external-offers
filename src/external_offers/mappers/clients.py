from cian_entities import EntityMapper

from external_offers.entities import Client


client_mapper = EntityMapper(
    Client,
    without_camelcase=True,
)
