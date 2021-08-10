CREATE TYPE offer_status_type AS enum (
    'waiting',
    'inProgress',
    'draft',
    'callMissed',
    'callLater',
    'cancelled',
    'declined',
    'alreadyPublished',
    'phoneUnavailable',
    'callInterrupted',
    'promoGiven'
);
CREATE TYPE offer_publication_status_type AS enum (
    'Draft',
    'Published',
    'Deactivated',
    'Refused',
    'Deleted',
    'Sold',
    'Moderate',
    'RemovedByModerator',
    'Blocked'
);
CREATE TYPE client_status_type AS enum (
    'waiting',
    'declined',
    'inProgress',
    'callLater',
    'callMissed',
    'accepted',
    'phoneUnavailable',
    'callInterrupted',
    'promoGiven'
);

CREATE TABLE offers_for_call
(
    id            varchar                  not null primary key,
    parsed_id     varchar                  not null,
    offer_cian_id bigint,
    client_id     int                      not null,
    status        offer_status_type        not null,
    publication_status offer_publicattion_status_type  null,
    created_at    timestamp with time zone not null,
    synced_at     timestamp with time zone not null,
    started_at    timestamp with time zone,
    promocode     varchar,
    priority      int,
    category      varchar,
    last_call_id  varchar,
    row_version         bigint                   not null default 0,
    synced_with_kafka   boolean                  not null default false,
    synced_with_grafana boolean                  not null default false,
    parsed_created_at   timestamp with time zone not null default current_timestamp
);

CREATE TABLE clients
(
    client_id        varchar     not null primary key,
    avito_user_id    varchar     not null,
    cian_user_id     bigint,
    client_name      varchar,
    client_phones    varchar[]   not null,
    client_email     varchar(50),
    operator_user_id bigint,
    status           client_status_type,
    segment          varchar(1),
    next_call        timestamp with time zone,
    calls_count      smallint,
    last_call_id     varchar,
    comment          varchar,
    main_account_chosen  boolean  not null  default false,
    synced_with_grafana  boolean  not null  default false,
    unactivated          boolean  not null  default false
);

CREATE TABLE event_log
(
    id               serial primary key,
    offer_id         varchar                  not null,
    operator_user_id bigint,
    status           varchar(30)              not null,
    created_at       timestamp with time zone not null,
    last_call_id     varchar
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
    synced              boolean                  not null
);

CREATE INDEX ON clients(avito_user_id);