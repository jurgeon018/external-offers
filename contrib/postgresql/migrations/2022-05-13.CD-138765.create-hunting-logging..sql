CREATE TABLE hunted_client_logs (
	id serial
		constraint hunted_client_logs_pkey
			primary key,
    client_id varchar not null,
    is_returned_to_waiting boolean not null,
    operator_user_id bigint not null,
    created_at timestamp not null
);

CREATE TABLE hunted_count_logs (
    id serial
		constraint hunted_count_logs_pkey
			primary key,
    count bigint not null,
    operator_user_id bigint not null,
    created_at timestamp not null
);
