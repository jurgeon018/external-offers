-- Обновить командный приоритет у заданий со старым приоритетом 
update offers_for_call
set team_priorities = jsonb_set(team_priorities, '41', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'41'::text = '-1'
	limit 100000
)

update offers_for_call
set team_priorities = jsonb_set(team_priorities, '43', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'43'::text = '-1'
	limit 100000
)

update offers_for_call
set team_priorities = jsonb_set(team_priorities, '57', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'57'::text = '-1'
	limit 100000
)

update offers_for_call
set team_priorities = jsonb_set(team_priorities, '63', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'63'::text = '-1'
	limit 100000
)

update offers_for_call
set team_priorities = jsonb_set(team_priorities, '60', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'60'::text = '-1'
	limit 100000
)

update offers_for_call
set team_priorities = jsonb_set(team_priorities, '64', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'64'::text = '-1'
	limit 100000
)

update offers_for_call
set team_priorities = jsonb_set(team_priorities, '62', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'62'::text = '-1'
	limit 100000
)

update offers_for_call
set team_priorities = jsonb_set(team_priorities, '65', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'65'::text = '-1'
	limit 100000
)

update offers_for_call
set team_priorities = jsonb_set(team_priorities, '50', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'50'::text = '-1'
	limit 100000
)

update offers_for_call
set team_priorities = jsonb_set(team_priorities, '42', '999999999999999999', true)
where id in (
	select id
	from offers_for_call
	where team_priorities->>'42'::text = '-1'
	limit 100000
)

-- Добавить индексы на командные приоритеты для быстрой выдачи задания
create index offers_for_call_team_priority_41_created_at_idx on offers_for_call ((team_priorities -> '41'), created_at DESC);
create index offers_for_call_team_priority_43_created_at_idx on offers_for_call ((team_priorities -> '43'), created_at DESC);
create index offers_for_call_team_priority_57_created_at_idx on offers_for_call ((team_priorities -> '57'), created_at DESC);
create index offers_for_call_team_priority_63_created_at_idx on offers_for_call ((team_priorities -> '63'), created_at DESC);
create index offers_for_call_team_priority_60_created_at_idx on offers_for_call ((team_priorities -> '60'), created_at DESC);
create index offers_for_call_team_priority_64_created_at_idx on offers_for_call ((team_priorities -> '64'), created_at DESC);
create index offers_for_call_team_priority_62_created_at_idx on offers_for_call ((team_priorities -> '62'), created_at DESC);
create index offers_for_call_team_priority_65_created_at_idx on offers_for_call ((team_priorities -> '65'), created_at DESC);
create index offers_for_call_team_priority_50_created_at_idx on offers_for_call ((team_priorities -> '50'), created_at DESC);
create index offers_for_call_team_priority_42_created_at_idx on offers_for_call ((team_priorities -> '42'), created_at DESC);
