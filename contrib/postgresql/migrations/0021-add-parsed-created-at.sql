ALTER TABLE offers_for_call ADD COLUMN parsed_created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT current_timestamp;
