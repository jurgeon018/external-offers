from external_offers.repositories.postgresql.clients import (
    assign_waiting_client_to_operator,
    get_client_by_operator,
    set_client_to_call_missed_status,
    set_client_to_decline_status,
)
from external_offers.repositories.postgresql.offers import (
    exists_offers_in_progress_by_operator,
    exists_offers_in_progress_by_operator_and_offer_id,
    get_offers_in_progress_by_operator,
    set_offers_call_missed_by_client,
    set_offers_declined_by_client,
    set_waiting_offers_in_progress_by_client,
)
from external_offers.repositories.postgresql.parsed_offers import (
    get_parsed_offer_object_model_by_offer_for_call_id,
    save_parsed_offer,
)
