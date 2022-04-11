ALTER TABLE offers_for_call ADD COLUMN source_object_id VARCHAR;

UPDATE offers_for_call
SET source_object_id = parsed_offers.source_object_id
FROM parsed_offers
WHERE offers_for_call.parsed_id = parsed_offers.id;
