DROP TABLE status_history;

CREATE TABLE event_log
(
    id               serial primary key,
    offer_id         varchar                  not null,
    operator_user_id bigint,
    status           varchar(10)              not null,
    created_at       timestamp with time zone not null
);
