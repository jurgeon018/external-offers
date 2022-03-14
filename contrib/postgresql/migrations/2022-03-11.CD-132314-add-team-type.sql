CREATE TYPE team_type_enum AS enum (
    'hunter',
    'attractor'
);

ALTER TABLE teams ADD COLUMN team_type team_type_enum NOT NULL DEFAULT 'attractor';
ALTER TABLE clients ADD COLUMN real_phone VARCHAR;
ALTER TABLE clients ADD COLUMN real_name VARCHAR;
ALTER TABLE clients ADD COLUMN real_phone_hunted_at TIMESTAMP WITH TIME ZONE;
