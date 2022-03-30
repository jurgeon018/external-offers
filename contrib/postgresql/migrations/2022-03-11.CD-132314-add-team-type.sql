CREATE TYPE team_type_enum AS enum (
    'hunter',
    'attractor'
);

ALTER TABLE clients ADD COLUMN real_phone VARCHAR;
ALTER TABLE clients ADD COLUMN real_name VARCHAR;
ALTER TABLE clients ADD COLUMN real_phone_hunted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE teams ADD COLUMN team_type team_type_enum NULL;
UPDATE teams SET team_type='attractor'; 
ALTER TABLE teams ALTER COLUMN team_type SET NOT NULL;
