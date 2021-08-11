from cian_entities import EntityMapper

from external_offers.entities import (
    Client,
    ClientWaitingOffersCount,
    ClientDraftOffersCount,
)


client_mapper = EntityMapper(
    Client,
    without_camelcase=True,
)

client_waiting_offers_count_mapper = EntityMapper(
    ClientWaitingOffersCount,
    without_camelcase=True,
)

client_draft_offers_count_mapper = EntityMapper(
    ClientDraftOffersCount,
    without_camelcase=True,
)
