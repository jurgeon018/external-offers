from cian_entities import EntityMapper

from external_offers.entities import EnrichedEventLogEntry, EventLogEntry


enriched_event_log_entry_mapper = EntityMapper(
    EnrichedEventLogEntry,
    without_camelcase=True,
)

event_log_entry_mapper = EntityMapper(
    EventLogEntry,
    without_camelcase=True,
)
