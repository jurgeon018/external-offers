CREATE TYPE client_status_type AS enum (
    'active',
    'declined'
);

ALTER TABLE clients ADD COLUMN status client_status_type not null;
