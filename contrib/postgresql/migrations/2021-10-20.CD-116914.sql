ALTER TABLE offers_for_call ADD COLUMN team_priorities jsonb;
ALTER TABLE clients ADD COLUMN team_id INT DEFAULT NULL;