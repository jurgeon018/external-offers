CREATE TABLE account_priorities
(
    priority_id SERIAL  NOT NULL PRIMARY KEY,
    smb_account_priority       INT NOT NULL,
    homeowner_account_priority INT NOT NULL,
    phone         VARCHAR NOT NULL UNIQUE,
    created_at    timestamp with time zone NOT NULL,
    updated_at    timestamp with time zone NOT NULL
)
