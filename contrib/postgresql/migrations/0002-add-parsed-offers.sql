create table parsed_offers
(
    id                  varchar unique primary key,
    user_segment        varchar                  not null,
    source_object_id    varchar                  not null,
    source_user_id      varchar                  not null,
    source_object_model json                     not null,
    is_calltracking     boolean                  not null,
    timestamp           timestamp with time zone not null,
    created_at          timestamp with time zone not null,
    updated_at          timestamp with time zone not null
);