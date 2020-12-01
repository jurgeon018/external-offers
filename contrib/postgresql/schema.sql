CREATE TYPE offer_status_type AS enum (
    'waiting',
    'inProgress',
    'draft',
    'callMissed',
    'cancelled',
    'declined',
    'done'
    );

CREATE TYPE client_status_type AS enum (
    'waiting',
    'declined',
    'inProgress',
    'callRetry',
    'callMissed',
    'accepted'
    );

CREATE TABLE offers_for_call
(
    id            varchar                  not null primary key,
    parsed_id     varchar                  not null,
    offer_cian_id bigint,
    client_id     int                      not null,
    status        offer_status_type        not null,
    created_at    timestamp with time zone not null,
    synced_at     timestamp with time zone not null,
    started_at    timestamp with time zone,
    promocode     varchar
);

CREATE TABLE clients
(
    client_id        varchar     not null primary key,
    avito_user_id    varchar     not null,
    realty_user_id   bigint,
    client_name      varchar(100) not null,
    client_phones    varchar[]   not null,
    client_email     varchar(50),
    operator_user_id bigint,
    status           client_status_type

);

CREATE TABLE event_log
(
    id               serial primary key,
    offer_id         varchar                  not null,
    operator_user_id bigint,
    status           varchar(10)              not null,
    created_at       timestamp with time zone not null
);


create table parsed_offers
(
    id                  varchar unique primary key,
    user_segment        varchar,
    source_object_id    varchar,
    source_user_id      varchar                  not null,
    source_object_model jsonb                    not null,
    is_calltracking     boolean                  not null,
    timestamp           timestamp with time zone not null,
    created_at          timestamp with time zone not null,
    updated_at          timestamp with time zone not null,
    synced              boolean                  not null,
);
