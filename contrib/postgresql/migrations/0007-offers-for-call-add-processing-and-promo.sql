ALTER TABLE offers_for_call ADD COLUMN promocode varchar;
ALTER TABLE parsed_offers ADD COLUMN user_synced BOOLEAN NOT NULL DEFAULT FALSE;
