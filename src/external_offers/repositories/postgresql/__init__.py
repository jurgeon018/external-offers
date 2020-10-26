from external_offers.repositories.postgresql.clients import assign_waiting_client_to_operator, get_client_by_operator
from external_offers.repositories.postgresql.offers import (
    exists_offers_in_progress_by_operator,
    get_offers_in_progress_by_operator,
    set_waiting_offers_in_progress_by_client,
)
