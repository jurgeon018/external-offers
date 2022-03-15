-- индексы для условий выборки в assign_suitable_client_to_operator

create index clients_real_phone_hunted_at_index
	on clients (real_phone_hunted_at);

create index clients_real_phone_index
	on clients (real_phone);

-- при джоине offers_for_call + parsed_offers
create index offers_for_call_parsed_id_index
	on offers_for_call (parsed_id);
