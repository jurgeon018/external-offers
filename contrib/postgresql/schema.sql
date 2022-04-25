CREATE TYPE team_type_enum AS enum (
    'hunter',
    'attractor'
);


create table offers_for_call
(
	id varchar not null
		constraint offers_for_call_pkey
			primary key,
	parsed_id varchar not null,
	source_object_id varchar,
	offer_cian_id bigint,
	is_calltracking boolean,
	client_id varchar not null,
	status offer_status_type not null,
	created_at timestamp with time zone not null,
	started_at timestamp with time zone,
	synced_at timestamp with time zone not null,
	promocode varchar,
	priority bigint,
	last_call_id varchar,
	parsed_created_at timestamp with time zone default CURRENT_TIMESTAMP not null,
	category varchar,
	synced_with_kafka boolean default false,
	synced_with_grafana boolean default false not null,
	is_test boolean default false not null,
	publication_status offer_publication_status_type,
	row_version bigint default 0 not null,
	external_offer_type varchar,
	team_priorities jsonb,
	comment varchar,
	group_id varchar
);

create index offers_for_call_offer_cian_id_idx
	on offers_for_call (offer_cian_id);

create index offers_for_call_client_id_idx
	on offers_for_call (client_id);

create table clients
(
	client_id varchar not null
		constraint clients_pkey
			primary key,
	avito_user_id varchar not null,
	cian_user_id bigint,
	client_name varchar,
	client_email varchar(50),
	operator_user_id bigint,
	hunter_user_id bigint,
	status client_status_type,
	client_phones character varying[] not null,
	real_phone varchar,
	real_name varchar,
	real_phone_hunted_at timestamp,
	segment varchar(255),
	next_call timestamp with time zone,
	last_call_id varchar,
	calls_count smallint,
	main_account_chosen boolean default false not null,
	synced_with_grafana boolean default false not null,
	comment varchar,
	is_test boolean default false not null,
	unactivated boolean default false not null,
	reason_of_decline varchar,
	additional_numbers varchar,
	additional_emails varchar,
	team_id integer,
	subsegment varchar
);

create index clients_avito_user_id_idx
	on clients (avito_user_id);

create table tmp_parsed_offers
(
	id varchar,
	user_segment varchar,
	source_object_id varchar,
	source_user_id varchar,
	source_object_model json,
	is_calltracking boolean,
	timestamp timestamp with time zone,
	created_at timestamp with time zone,
	updated_at timestamp with time zone
);

create table event_log
(
	id serial
		constraint event_log_pkey
			primary key,
	offer_id varchar not null,
	operator_user_id bigint,
	status varchar(30) not null,
	created_at timestamp with time zone not null,
	call_id varchar
);

create table parsed_offers
(
	id varchar,
	user_segment varchar,
	source_object_id varchar
		constraint source_object_id_unique
			unique,
	source_user_id varchar,
	source_object_model jsonb,
	is_calltracking boolean,
	timestamp timestamp with time zone,
	created_at timestamp with time zone,
	updated_at timestamp with time zone,
	synced boolean default false,
	is_test boolean default false not null,
	external_offer_type varchar,
	source_group_id varchar,
	user_subsegment varchar
);

create index parsed_offers_id_idx
	on parsed_offers (id);

create table ct_phones
(
	phone varchar
);

create table teams
(
	team_id serial
		constraint teams_pkey
			primary key,
	team_name varchar
		constraint teams_team_name_key
			unique,
	lead_id varchar not null,
	segment segment_type,
	settings jsonb,
	team_type team_type_enum not null
);

create table operators
(
	operator_id varchar not null
		constraint operators_pkey
			primary key,
	is_teamlead boolean not null,
	full_name varchar,
	team_id integer,
	email varchar,
	created_at timestamp with time zone not null,
	updated_at timestamp with time zone not null
);

create table calltracking_phone_numbers
(
	phone varchar not null
);

create table client_account_statuses
(
	phone varchar not null
		constraint client_account_statuses_pkey
			primary key,
	smb_account_status varchar,
	homeowner_account_status varchar,
	new_cian_user_id bigint,
	created_at timestamp with time zone not null,
	updated_at timestamp with time zone not null
);
