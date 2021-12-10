CREATE TABLE phones_statuses
(
    smb_account_status       VARCHAR NOT NULL,
    homeowner_account_status VARCHAR NOT NULL,
    phone         VARCHAR NOT NULL PRIMARY KEY UNIQUE,
    new_cian_user_id VARCHAR NULL,
    created_at    timestamp with time zone NOT NULL,
    updated_at    timestamp with time zone NOT NULL
)
