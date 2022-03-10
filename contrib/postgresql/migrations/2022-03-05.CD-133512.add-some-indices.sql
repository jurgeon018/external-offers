-- добавил индекс для джойна
create index offers_for_call_client_id_index
	on offers_for_call (client_id);

-- добавил индекс для условий выборки
create index clients_operator_user_id_index
	on clients (operator_user_id nulls first);

-- добавил индекс для сортировки
create index offers_for_call_priority_created_at_index
	on offers_for_call (priority asc nulls last, created_at desc);
