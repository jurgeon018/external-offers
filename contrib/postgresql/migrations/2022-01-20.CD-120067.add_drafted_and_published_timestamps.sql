alter table clients add column drafted_at timestamp with time zone;
alter table clients add column published_at timestamp with time zone;
alter table offers_for_call add column drafted_at timestamp with time zone;
alter table offers_for_call add column published_at timestamp with time zone;
