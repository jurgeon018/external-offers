from external_offers.repositories.postgresql.clients import (
    assign_client_to_operator_and_increase_calls_count,
    assign_suitable_client_to_operator,
    delete_waiting_clients_by_client_ids,
    get_cian_user_id_by_client_id,
    get_client_by_avito_user_id,
    get_client_by_client_id,
    get_client_for_update_by_phone_number,
    get_client_in_progress_by_operator,
    get_segment_by_client_id,
    save_client,
    set_cian_user_id_by_client_id,
    set_client_accepted_and_no_operator_if_no_offers_in_progress,
    set_client_to_call_interrupted_status_and_return,
    set_client_to_call_later_status_set_next_call_and_return,
    set_client_to_call_missed_status_set_next_call_and_return,
    set_client_to_decline_status_and_return,
    set_client_to_phone_unavailable_status_and_return,
    set_client_to_promo_given_status_and_return,
    set_client_to_waiting_status_and_return,
    set_main_cian_user_id_by_client_id,
    set_phone_number_by_client_id,
)
from external_offers.repositories.postgresql.event_log import (
    get_enriched_event_log_entries_for_calls_kafka_sync,
    get_enriched_event_log_entries_for_drafts_kafka_sync,
    save_event_log_for_offers,
)
from external_offers.repositories.postgresql.grafana_objects import (
    fetch_segmented_objects,
    get_processed_synced_objects_count,
    get_synced_objects_count,
    get_unsynced_waiting_objects_count,
    sync_waiting_objects_with_grafana,
    unsync_objects_with_grafana,
)
from external_offers.repositories.postgresql.offers import (
    delete_old_waiting_offers_for_call,
    delete_waiting_clients_with_count_off_limit,
    delete_waiting_offers_for_call_by_client_ids,
    delete_waiting_offers_for_call_by_parsed_ids,
    delete_waiting_offers_for_call_with_count_off_limit,
    delete_waiting_offers_for_call_without_parsed_offers,
    exists_offers_draft_by_client,
    exists_offers_in_progress_by_client,
    exists_offers_in_progress_by_operator,
    exists_offers_in_progress_by_operator_and_offer_id,
    get_enriched_offers_in_progress_by_operator,
    get_last_sync_date,
    get_offer_by_offer_id,
    get_offer_by_parsed_id,
    get_offer_cian_id_by_offer_id,
    get_offer_promocode_by_offer_id,
    get_offers_in_progress_by_operator,
    get_offers_parsed_ids_by_parsed_ids,
    get_offers_regions_by_client_id,
    get_unactivated_clients_counts_by_clients,
    get_waiting_offer_counts_by_clients,
    get_offers_for_prioritization_by_client_ids,
    iterate_over_offers_for_call_sorted,
    save_offer_for_call,
    set_offer_already_published_by_offer_id,
    set_offer_cancelled_by_offer_id,
    set_offer_cian_id_by_offer_id,
    set_offer_draft_by_offer_id,
    set_offer_promocode_by_offer_id,
    set_offers_call_interrupted_by_client,
    set_offers_call_later_by_client,
    set_offers_call_missed_by_client,
    set_offers_declined_by_client,
    set_offers_in_progress_by_client,
    set_offers_phone_unavailable_by_client,
    set_offers_promo_given_by_client,
    set_waiting_offers_priority_by_offer_ids,
    sync_offers_for_call_with_kafka_by_ids,
    try_to_lock_offer_and_return_status,
)
from external_offers.repositories.postgresql.parsed_offers import (
    delete_outdated_parsed_offers,
    get_lastest_event_timestamp,
    get_latest_updated_at,
    get_parsed_offer_object_model_by_offer_id,
    iterate_over_parsed_offers_sorted,
    save_parsed_offer,
    set_synced_and_fetch_parsed_offers_chunk,
    update_offer_categories_by_offer_id,
)
