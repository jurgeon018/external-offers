CREATE TYPE offer_status_type_new AS enum (
    'waiting',
    'inProgress',
    'draft',
    'callMissed',
    'callLater',
    'cancelled',
    'declined',
    'alreadyPublished',
    'phoneUnavailable',
    'callInterrupted',
    'promoGiven'
);

CREATE TYPE client_status_type_new AS enum (
    'waiting',
    'declined',
    'inProgress',
    'callLater',
    'callMissed',
    'accepted',
    'phoneUnavailable',
    'callInterrupted',
    'promoGiven'
);


ALTER TABLE offers_for_call ALTER COLUMN status TYPE offer_status_type_new USING status::text::offer_status_type_new;
ALTER TABLE clients ALTER COLUMN status TYPE client_status_type_new USING status::text::client_status_type_new;

DROP TYPE offer_status_type;
DROP TYPE client_status_type;

ALTER TYPE offer_status_type_new RENAME TO offer_status_type;
ALTER TYPE client_status_type_new RENAME TO client_status_type;

ALTER TABLE event_log ALTER COLUMN status TYPE varchar(30);
