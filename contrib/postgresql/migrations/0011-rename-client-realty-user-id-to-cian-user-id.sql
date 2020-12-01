ALTER TABLE clients RENAME COLUMN realty_user_id TO cian_user_id;

ALTER TABLE clients ALTER COLUMN client_name TYPE varchar(100);
