from cian_entities.mappers import EntityMapper, ValueMapper

from external_offers.services.calls_history.search import CallsHistorySearch


calls_history_mapper = EntityMapper(
    CallsHistorySearch,
    without_camelcase=True,
    mappers={
        'time_from': ValueMapper(),
        'time_to': ValueMapper(),
    }
)
