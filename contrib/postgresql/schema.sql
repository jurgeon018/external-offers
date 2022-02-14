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
    'promoGiven',
    'done'
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
    publication_status offer_publication_status_type  null,
    created_at    timestamp with time zone not null,
    synced_at     timestamp with time zone not null,
    started_at    timestamp with time zone,
    promocode     varchar,
    priority      int,
    team_priorities jsonb,
    category      varchar,
    last_call_id  varchar,
    comment       varchar,
    group_id      varchar,
    row_version         bigint                   not null default 0,
    synced_with_kafka   boolean                  not null default false,
    synced_with_grafana boolean                  not null default false,
    is_test             boolean                  not null default false,
    parsed_created_at   timestamp with time zone not null default current_timestamp,
    external_offer_type varchar,
    drafted_at          timestamp with time zone,
    published_at        timestamp with time zone
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
    segment          varchar(255),
    subsegment       varchar,
    next_call        timestamp with time zone,
    unactivated_at   timestamp with time zone,
    calls_count      smallint,
    last_call_id     varchar,
    comment          varchar,
    team_id          int default null,
    reason_of_decline varchar default null,
    additional_numbers varchar default null,
    additional_emails varchar default null,
    main_account_chosen  boolean  not null  default false,
    synced_with_grafana  boolean  not null  default false,
    unactivated          boolean  not null  default false,
    is_test              boolean  not null  default false,
    drafted_at           timestamp with time zone,
    published_at         timestamp with time zone
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
    user_subsegment     varchar,
    source_object_id    varchar,
    source_group_id     varchar,
    source_user_id      varchar                  not null,
    source_object_model jsonb                    not null,
    is_calltracking     boolean                  not null,
    timestamp           timestamp with time zone not null,
    created_at          timestamp with time zone not null,
    updated_at          timestamp with time zone not null,
    is_test             boolean                  not null default false,
    synced              boolean                  not null,
    external_offer_type varchar
);

CREATE INDEX ON clients(avito_user_id);
CREATE INDEX ON offers_for_call(offer_cian_id);
CREATE INDEX ON offers_for_call(client_id); 
CREATE INDEX ON event_log(created_at); 
ALTER TABLE parsed_offers ADD CONSTRAINT source_object_id_unique UNIQUE(source_object_id);

CREATE TYPE segment_type AS enum (
	'a',
	'b',
	'c',
	'd',
	'commercial'
);

CREATE TABLE teams
(
    team_id   SERIAL  NOT NULL PRIMARY KEY,
    team_name VARCHAR UNIQUE,
    lead_id   VARCHAR        NOT NULL,
    segment   segment_type,
    settings  JSONB
);

CREATE TABLE operators
(
    operator_id VARCHAR UNIQUE NOT NULL PRIMARY KEY,
    is_teamlead BOOLEAN        NOT NULL,
    full_name   VARCHAR,
    team_id     INT,
    email       VARCHAR,
    created_at    timestamp with time zone not null,
    updated_at    timestamp with time zone not null
);

CREATE TABLE client_account_statuses
(
    phone         VARCHAR NOT NULL PRIMARY KEY UNIQUE,
    smb_account_status       VARCHAR,
    homeowner_account_status VARCHAR,
    new_cian_user_id BIGINT NULL,
    created_at    timestamp with time zone NOT NULL,
    updated_at    timestamp with time zone NOT NULL
)

CREATE TABLE clients_priorities
(
    priorities jsonb,
    team_id    int default null,
    created_at timestamp with time zone NOT NULL,
    updated_at timestamp with time zone NOT NULL
)
