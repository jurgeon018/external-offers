from cian_entities import EntityMapper

from external_offers.entities import EnrichedEventLogEntry


enriched_event_log_entry_mapper = EntityMapper(
    EnrichedEventLogEntry,
    without_camelcase=True,
)

