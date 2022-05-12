ALTER TABLE clients ADD COLUMN synced_with_kafka BOOLEAN NULL;
UPDATE clients SET synced_with_kafka='f';