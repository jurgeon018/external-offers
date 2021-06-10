ALTER TABLE offers_for_call ADD COLUMN category varchar;
UPDATE offers_for_call
SET category = parsed_offers.source_object_model->>'category'
FROM parsed_offers
WHERE offers_for_call.parsed_id = parsed_offers.id
AND offers_for_call.status = 'waiting';
