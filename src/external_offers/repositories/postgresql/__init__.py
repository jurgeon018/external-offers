from external_offers.repositories.postgresql.clients import (
    assign_waiting_client_to_operator,
    delete_waiting_clients_by_client_ids,
    exists_waiting_client,
    get_cian_user_id_by_client_id,
    get_client_by_avito_user_id,
    get_client_by_client_id,
    get_client_by_operator,
    get_client_id_by_offer_id,
    save_client,
    set_cian_user_id_by_client_id,
    set_client_accepted_and_no_operator_if_no_offers_in_progress,
    set_client_to_call_later_status_and_return,
    set_client_to_call_missed_status_and_return,
    set_client_to_decline_status_and_return,
    set_client_to_waiting_status_and_return,
)
from external_offers.repositories.postgresql.event_log import (
    get_enriched_event_log_entries_for_calls_kafka_sync,
    get_enriched_event_log_entries_for_drafts_kafka_sync,
    save_event_log_for_offers,
)
from external_offers.repositories.postgresql.offers import (
    delete_waiting_clients_with_count_off_limit,
    delete_waiting_offers_for_call_by_client_ids,
    delete_waiting_offers_for_call_with_count_off_limit,
    exists_offers_in_progress_by_client,
    exists_offers_in_progress_by_operator,
    exists_offers_in_progress_by_operator_and_offer_id,
    exists_offers_draft_by_client,
    get_enriched_offers_in_progress_by_operator,
    get_last_sync_date,
    get_offer_by_parsed_id,
    get_offer_cian_id_by_offer_id,
    get_offer_promocode_by_offer_id,
    get_offers_in_progress_by_operator,
    get_offers_parsed_ids_by_parsed_ids,
    get_waiting_offer_counts_by_clients,
    save_offer_for_call,
    set_offer_cancelled_by_offer_id,
    set_offer_cian_id_by_offer_id,
    set_offer_draft_by_offer_id,
    set_offer_promocode_by_offer_id,
    set_offers_call_later_by_client,
    set_offers_call_missed_by_client,
    set_offers_declined_by_client,
    set_waiting_offers_in_progress_by_client,
    set_waiting_offers_priority_by_client_ids,
    try_to_lock_offer_and_return_status,
)
from external_offers.repositories.postgresql.parsed_offers import (
    get_lastest_event_timestamp,
    get_parsed_offer_object_model_by_offer_id,
    save_parsed_offer,
    set_synced_and_fetch_parsed_offers_chunk,
)
