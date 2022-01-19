CREATE TABLE client_account_statuses
(
    phone         VARCHAR NOT NULL PRIMARY KEY UNIQUE,
    smb_account_status       VARCHAR,
    homeowner_account_status VARCHAR,
    new_cian_user_id BIGINT NULL,
    created_at    timestamp with time zone NOT NULL,
    updated_at    timestamp with time zone NOT NULL
)
