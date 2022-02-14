CREATE TABLE clients_priorities
(
    priorities jsonb,
    team_id    int default null,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
)
