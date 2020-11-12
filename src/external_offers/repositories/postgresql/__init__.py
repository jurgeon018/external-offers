from external_offers.repositories.postgresql.clients import (
    assign_waiting_client_to_operator,
    get_client_by_avito_user_id,
    get_client_by_operator,
    get_client_id_by_offer_id,
    get_realty_user_id_by_client_id,
    save_client,
    set_client_to_call_missed_status,
    set_client_to_decline_status,
    set_client_to_waiting_status,
    set_realty_user_id_by_client_id,
)
from external_offers.repositories.postgresql.offers import (
    exists_offers_in_progress_by_client,
    exists_offers_in_progress_by_operator,
    exists_offers_in_progress_by_operator_and_offer_id,
    get_last_sync_date,
    get_offer_cian_id_by_offer_id,
    get_offers_by_parsed_id,
    get_offers_in_progress_by_operator,
    save_offer_for_call,
    set_offer_cancelled_by_offer_id,
    set_offer_cian_id_by_offer_id,
    set_offer_draft_by_offer_id,
    set_offers_call_missed_by_client,
    set_offers_declined_by_client,
    set_waiting_offers_in_progress_by_client,
)
from external_offers.repositories.postgresql.parsed_offers import (
    get_parsed_offer_object_model_by_offer_id,
    save_parsed_offer,
    set_synced_and_fetch_parsed_offers_chunk,
)
