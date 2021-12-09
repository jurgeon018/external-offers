CREATE TABLE account_priorities
(
    priority_id SERIAL  NOT NULL PRIMARY KEY,
    client_id   VARCHAR NOT NULL,
    team_id     INT         NULL,
    priority    INT     NOT NULL,
    created_at    timestamp with time zone NOT NULL,
    updated_at    timestamp with time zone NOT NULL,
    UNIQUE (client_id, team_id)
)
