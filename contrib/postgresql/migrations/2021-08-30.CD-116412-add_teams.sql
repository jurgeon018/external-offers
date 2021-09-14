CREATE TYPE segment_type AS enum (
	'a',
	'b',
	'c',
	'd',
	'commercial'
);

CREATE TABLE teams
(
    team_id  VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    name     VARCHAR UNIQUE,
    lead_id  VARCHAR        NOT NULL,
    segment  segment_type,
    settings JSONB
);

CREATE TABLE operators
(
    operator_id VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    is_teamlead BOOLEAN        NOT NULL,
    name        VARCHAR,
    team_id     VARCHAR
);
