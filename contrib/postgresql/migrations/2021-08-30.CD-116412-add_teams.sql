CREATE TYPE segment_type AS enum (
	'a',
	'b',
	'c',
	'd',
	'commercial'
);

CREATE TABLE teams
(
    team_id   SERIAL  NOT NULL PRIMARY KEY,
    team_name VARCHAR UNIQUE,
    lead_id   VARCHAR        NOT NULL,
    segment   segment_type,
    settings  JSONB
);

CREATE TABLE operators
(
    operator_id VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    is_teamlead BOOLEAN        NOT NULL,
    full_name   VARCHAR,
    team_id     INT,
    email       VARCHAR,
    created_at    timestamp with time zone not null,
    updated_at    timestamp with time zone not null
);
