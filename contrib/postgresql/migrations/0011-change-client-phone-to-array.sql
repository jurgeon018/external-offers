ALTER TABLE clients DROP COLUMN client_phone;
ALTER TABLE clients ADD COLUMN client_phones varchar[] NOT NULL;
