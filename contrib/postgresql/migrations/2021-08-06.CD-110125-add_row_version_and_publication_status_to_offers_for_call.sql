CREATE TYPE offer_publication_status_type AS enum (
    'Draft',
    'Published',
    'Deactivated',
    'Refused',
    'Deleted',
    'Sold',
    'Moderate',
    'RemovedByModerator',
    'Blocked'
);

ALTER TABLE offers_for_call ADD COLUMN publication_status offer_publication_status_type;

ALTER TABLE offers_for_call ADD COLUMN row_version BIGINT NOT NULL DEFAULT 0;
