CREATE TYPE offer_status_type AS enum (
    'waiting',
    'inProgress',
    'draft',
    'callMissed',
    'cancelled',
    'declined',
    'done'
);

CREATE TABLE offers_for_call
(
    id                  int                       not null primary key,
    parsed_id           bigint                    not null,
    offer_cian_id       bigint,
    client_id           int                       not null,
    status              offer_status_type         not null,
    created_at          timestamp with time zone  not null,
    started_at          timestamp with time zone
);

CREATE TABLE clients
(
    client_id            int                      not null primary key,
    avito_user_id        bigint                   not null,
    realty_user_id       bigint,                   
    client_name          varchar(50)              not null,
    client_phone         varchar(12)              not null,
    client_email         varchar(50),
    operator_user_id     bigint

);

CREATE TABLE status_history
(
    id                   bigint                   not null primary key,
    offer_id             int                      not null,
    operator_user_id     bigint                   not null,
    previous_status     varchar(10)              not null,
    status               varchar(10)              not null,
    created_at           timestamp with time zone not null
);
