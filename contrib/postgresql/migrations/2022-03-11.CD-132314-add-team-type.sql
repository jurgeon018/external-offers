CREATE TYPE team_type_enum AS enum (
    'hunter',
    'attractor'
);

ALTER TABLE teams ADD COLUMN team_type team_type_enum NOT NULL DEFAULT 'attractor';
