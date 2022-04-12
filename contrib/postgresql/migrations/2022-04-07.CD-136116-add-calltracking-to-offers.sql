ALTER TABLE offers_for_call ADD COLUMN is_calltracking BOOLEAN;

UPDATE offers_for_call
SET is_calltracking = parsed_offers.is_calltracking
FROM parsed_offers
WHERE offers_for_call.parsed_id = parsed_offers.id;

CREATE INDEX clients_real_phone_hunted_at_idx ON clients (real_phone_hunted_at);
