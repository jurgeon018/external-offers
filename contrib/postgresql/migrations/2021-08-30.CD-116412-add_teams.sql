CREATE TYPE segment_type AS enum (
	'a',
	'b',
	'c',
	'd',
	'commercial'
);

CREATE TABLE teams
(
    id       VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    name     VARCHAR UNIQUE NULL,
    lead_id  VARCHAR        NOT NULL,
    segment  segment_type   NULL,
    settings JSONB          NULL
);

CREATE TABLE operators
(
    id          VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    name        VARCHAR        NULL,
    team_id     VARCHAR        NULL,
    is_teamlead BOOLEAN        NOT NULL DEFAULT FALSE,
    role_id     VARCHAR        NULL
);
