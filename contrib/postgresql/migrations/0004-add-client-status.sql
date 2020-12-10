CREATE TYPE client_status_type AS enum (
    'waiting',
    'declined',
    'inProgress',
    'callLater',
    'callMissed',
    'accepted'
);

ALTER TABLE clients ADD COLUMN status client_status_type not null;
