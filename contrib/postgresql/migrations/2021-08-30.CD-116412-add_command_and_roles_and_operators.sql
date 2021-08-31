
CREATE TYPE segment_type AS enum (
	'all',
	'a',
	'b',
	'c',
	'd',
	'commercial'
);

CREATE TABLE roles (
    id VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    segment segment_type NOT NULL DEFAULT 'all'
);

CREATE TABLE teams
(
    id VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    name VARCHAR UNIQUE,
    role_id VARCHAR,
    settings JSONB
);

CREATE TABLE operators
(
    id VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    name VARCHAR
    team_id VARCHAR,
    is_teamlead BOOLEAN NOT NULL DEFAULT FALSE
);
