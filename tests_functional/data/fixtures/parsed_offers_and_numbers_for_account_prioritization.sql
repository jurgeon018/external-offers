INSERT INTO client_account_statuses (
    phone, smb_account_status, homeowner_account_status, new_cian_user_id, updated_at, created_at    
) VALUES
('+70000', '-1', '-1', NULL, now() - interval '10 day', now() - interval '100 days'),
('+70001', '-1', '-1', NULL, now() - interval '7 day',  now() - interval '70 days'),
('+70002', '-1', '-1', NULL, now() - interval '4 day',  now() - interval '40 days'),
('+70003', '-1', '-1', NULL, now() - interval '2 day',  now() - interval '100 days'),
('+70004', '-1', '-1', NULL, now() - interval '1 day',  now() - interval '100 days'),
('+70005', '-1', '-1', NULL, now(),                     now() - interval '100 days');

INSERT INTO parsed_offers (
    id,
    user_segment, user_subsegment,
    source_object_id, source_user_id,
    source_object_model, source_group_id,
    is_calltracking, synced, is_test, timestamp, created_at, updated_at, external_offer_type
) VALUES
-- user_segment = 'c'
(
    '1',
    'c', NULL,
    '1', '1',
    '{"region":"4150", "phones":["+700000001"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '2',
    'c', NULL,
    '2', '2',
    '{"region":"4150", "phones":["+700000002"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '3',
    'c', NULL,
    '3', '3',
    '{"region":"4150", "phones":["+700000003"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '4',
    'c', NULL,
    '4', '4',
    '{"region":"4150", "phones":["+700000004"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
-- user_segment = 'd'
(
    '12',
    'd', NULL,
    '12', '12',
    '{"region":"4150", "phones":["+700000012"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '13',
    'd', NULL,
    '13', '13',
    '{"region":"4150", "phones":["+700000013"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '14',
    'd', NULL,
    '14', '14',
    '{"region":"4150", "phones":["+700000014"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
-- невалидные значения
(
    '5',
    NULL, NULL,
    '5', '5',
    '{"region":"4150", "phones":["+700000005"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --user_segment is NULL - невалидное значение
),
(
    '6',
    'b', NULL,
    '6', '6',
    '{"region":"4150", "phones":["+700000006"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --user_segment == 'b' - невалидное значение
),
(
    '7',
    'c', NULL,
    '7', '7',
    '{"region":"4150", "phones":[]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --phones = [] - невалидное значение
),
(
    '8',
    'c', NULL,
    '8', '8',
    '{"region":"4150"}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --phones = null - невалидное значение
),
(
    '9',
    'c', NULL,
    '9', '9',
    '{"region":"4150", "phones":[""]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --phones = [''] - невалидное значение
),
(
    '10',
    'c', NULL,
    '10', NULL,
    '{"region":"4150", "phones":["+700000010"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --source_user_id NULL - невалидное значение
),
(
    '11',
    'c', NULL,
    '11', '11',
    '{"region":"4150", "phones":["+700000011"]}', NULL,
    't', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --is_calltrackng = 't' - невалидное значение
);
