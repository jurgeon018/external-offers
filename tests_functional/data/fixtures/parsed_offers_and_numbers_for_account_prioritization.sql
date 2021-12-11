INSERT INTO client_account_statuses (
    phone, smb_account_status, homeowner_account_status, new_cian_user_id, updated_at, created_at    
) VALUES
('+70000', NULL, NULL, NULL, now() - interval '10 day', now() - interval '100 days'),
('+70001', NULL, NULL, NULL, now() - interval '7 day',  now() - interval '70 days'),
('+70002', NULL, NULL, NULL, now() - interval '4 day',  now() - interval '40 days'),
('+70003', NULL, NULL, NULL, now() - interval '2 day',  now() - interval '100 days'),
('+70004', NULL, NULL, NULL, now() - interval '1 day',  now() - interval '100 days'),
('+70005', NULL, NULL, NULL, now(),                     now() - interval '100 days');

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
    '{"region":"4150", "phones":["+70000001"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '2',
    'c', NULL,
    '2', '2',
    '{"region":"4150", "phones":["+70000002"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '3',
    'c', NULL,
    '3', '3',
    '{"region":"4150", "phones":["+70000003"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '4',
    'c', NULL,
    '4', '4',
    '{"region":"4150", "phones":["+70000004"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '5',
    'c', NULL,
    '5', '5',
    '{"region":"4150", "phones":["+70000005"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '6',
    'c', NULL,
    '6', '6',
    '{"region":"4150", "phones":["+70000006"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '7',
    'c', NULL,
    '7', '7',
    '{"region":"4150", "phones":["+70000007"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
-- user_segment = 'd'
(
    '11',
    'd', NULL,
    '11', '11',
    '{"region":"4150", "phones":["+70000011"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '12',
    'd', NULL,
    '12', '12',
    '{"region":"4150", "phones":["+70000012"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '13',
    'd', NULL,
    '13', '13',
    '{"region":"4150", "phones":["+70000013"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '14',
    'd', NULL,
    '14', '14',
    '{"region":"4150", "phones":["+70000014"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '15',
    'd', NULL,
    '15', '15',
    '{"region":"4150", "phones":["+70000015"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '16',
    'd', NULL,
    '16', '16',
    '{"region":"4150", "phones":["+70000016"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '17',
    'd', NULL,
    '17', '17',
    '{"region":"4150", "phones":["+70000017"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
(
    '18',
    'd', NULL,
    '18', '18',
    '{"region":"4150", "phones":["+70000018"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
),
-- невалидные значения
(
    '95',
    NULL, NULL,
    '95', '95',
    '{"region":"4150", "phones":["+790000005"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --user_segment is NULL - невалидное значение
),
(
    '96',
    'b', NULL,
    '96', '96',
    '{"region":"4150", "phones":["+790000006"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --user_segment == 'b' - невалидное значение
),
(
    '97',
    'c', NULL,
    '97', '97',
    '{"region":"4150", "phones":[]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --phones = [] - невалидное значение
),
(
    '98',
    'c', NULL,
    '98', '98',
    '{"region":"4150"}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --phones = null - невалидное значение
),
(
    '99',
    'c', NULL,
    '99', '99',
    '{"region":"4150", "phones":[""]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --phones = [''] - невалидное значение
),
(
    '910',
    'c', NULL,
    '910', NULL,
    '{"region":"4150", "phones":["+790000910"]}', NULL,
    'f', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --source_user_id NULL - невалидное значение
),
(
    '911',
    'c', NULL,
    '911', '911',
    '{"region":"4150", "phones":["+790000911"]}', NULL,
    't', 'f', 'f', 'now()', 'now()', 'now()', NULL
    --is_calltrackng = 't' - невалидное значение
);
