INSERT INTO public.clients(
    client_id,
    avito_user_id,
    client_name,
    client_phones,
    client_email,
    operator_user_id,
    status,
    calls_count,
    last_call_id
) VALUES (
    '1',
    '32131322',
    'Александр Александров',
    '{+79812333234}',
    'testemail@gmail.com',
    60024635,
    'inProgress',
    1,
    NULL
), (
    '2',
    '32131323',
    'Александр Иванов',
    '{+79812333235}',
    'moyemail@gmail.com',
    NULL,
    'waiting',
    0,
    NULL
), (
    '3',
    '32131324',
    'Александр Петров',
    '{+79812333236}',
    'nemoyemail@gmail.com',
    NULL,
    'waiting',
    0,
    NULL
), (
    '4',
    '32131325',
    'Александр Петров',
    '{+79812333237}',
    'nemoyemail1234@gmail.com',
    60024638,
    'waiting',
    0,
    NULL
), (
    '5',
    '32131325',
    'Александр Петров',
    '{+79812333237}',
    'nemoyemail1234@gmail.com',
    60024649,
    'inProgress',
    1,
    NULL
), (
    '6',
    '32131326',
    'Александр Петров',
    '{+79812333238}',
    'nemoyemail1234@gmail.com',
    60024659,
    'inProgress',
    1,
    NULL
), (
    '7',
    '32131327',
    'Александр Александров',
    '{+79812932338}',
    'gmail@gmail.com',
    70024649,
    'inProgress',
    1,
    'last-call-id'
), (
    '8',
    '32131327',
    'Александр Александров',
    '{+79812932338}',
    'gmail@gmail.com',
    70024649,
    'waiting',
    1,
    'last-call-id'
), (
     '9',
    '321313279',
    'Александр Александров',
    '{+79812932338}',
    'commercial-alex@gmail.com',
    NULL,
    'waiting',
    1,
    'last-call-id'
);

INSERT INTO public.offers_for_call(
    id,
    parsed_id,
    client_id,
    status,
    created_at,
    started_at,
    synced_at,
    priority,
    last_call_id,
    synced_with_kafka,
    category
) VALUES (
    1,
    'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
    '1',
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    2,
    'f1a91ade-13a2-48d9-a05a-6131af39033e',
    '1',
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    3,
    'fbd30a97-7bed-4459-8cfd-8ba797ac9054',
    '2',
    'cancelled',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    4,
    '9999d421-b7ba-4ee0-b29f-bc8add87c933',
    '3',
    'waiting',
    '2020-10-10 04:05:06',
    '2020-10-10 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    5,
    '33e4d51e-e8d3-499d-9497-4229d6c539ee',
    '2',
    'waiting',
    '2020-10-12 03:05:06',
    '2020-10-12 03:05:06',
    '2020-10-12 03:05:06',
    2,
    NULL,
    false,
    NULL
), (
    6,
    'wrong-parsed-id',
    '4',
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    7,
    '1d6c73b8-3057-47cc-b50a-419052da619f',
    '4',
    'cancelled',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    8,
    '124c73b8-3057-47cc-b50a-419052da619f',
    '5',
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    9,
    '1dddd3b8-3057-47cc-b50a-419052da619f',
    '5',
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
),(
    10,
    'wrong-parsed-id-2',
    '4',
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
),(
    11,
    '2dddd3b8-3157-47cc-b50a-419052da619f',
    '6',
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    '2dddd3b8-3157-47cc-b50a-419052da6197',
    false,
    NULL
),(
    12,
    '3dddd3b8-3257345cc-b50a-419052da619f',
    '6',
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    '2dddd3b8-3157-47cc-b50a-419052da6197',
    false,
    NULL
),(
    13,
    '1d6c7dxc-3057-47cc-b50a-419052dfasf',
    '7',
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    'last-call-id',
    false,
    NULL
), (
    14,
    '1d6c7dxc-3057-47cc-b50a-419052da619f',
    '7',
    'draft',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    15,
    '1d6c7dxc-3057-47cc-b50a-419052da619f',
    '7',
    'callMissed',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    16,
    '1d6c7dxc-3057-47cc-b50a-419052da619f',
    '7',
    'callMissed',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
), (
    17,
    '1d6c7dxc-3057-47cc-b50a-419052da619f',
    '7',
    'callLater',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    'flatRent'
), (
    18,
    '1d6c7dxc-3057-47cc-b50a-419052da619f',
    '8',
    'waiting',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    'flatSale'
), (
    19,
    '1d6c7dxc-3057-47cc-b50a-419052da619f',
    '8',
    'waiting',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06',
    1,
    NULL,
    false,
    NULL
);





INSERT INTO public.parsed_offers (
    id,
    user_segment,
    source_object_id,
    source_user_id,
    source_object_model,
    is_calltracking,
    "timestamp",
    created_at,
    updated_at
) VALUES (
    '1dddd3b8-3057-47cc-b50a-419052da619f',
    'NOT_IMPORTANT',
    '1_1',
    '1',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    'fbd30a97-7bed-4459-8cfd-8ba797ac9054',
    'NOT_IMPORTANT',
    '1_2',
    '2',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    '9999d421-b7ba-4ee0-b29f-bc8add87c933',
    'NOT_IMPORTANT',
    '1_3',
    '3',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    '33e4d51e-e8d3-499d-9497-4229d6c539ee',
    'NOT_IMPORTANT',
    '1_4',
    '4',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    'wrong-parsed-id',
    'NOT_IMPORTANT',
    '1_5',
    '5',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    '1d6c73b8-3057-47cc-b50a-419052da619f',
    'NOT_IMPORTANT',
    '1_6',
    '6',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    '124c73b8-3057-47cc-b50a-419052da619f',
    'NOT_IMPORTANT',
    '1_7',
    '7',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    'wrong-parsed-id-2',
    'NOT_IMPORTANT',
    '1_8',
    '8',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    '2dddd3b8-3157-47cc-b50a-419052da619f',
    'NOT_IMPORTANT',
    '1_9',
    '9',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    '3dddd3b8-3257345cc-b50a-419052da619f',
    'NOT_IMPORTANT',
    '1_10',
    '10',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    '1d6c7dxc-3057-47cc-b50a-419052da619f',
    'NOT_IMPORTANT',
    '1_11',
    '11',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
    'NOT_IMPORTANT',
    '1_12',
    '12',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
),(
    'f1a91ade-13a2-48d9-a05a-6131af39033e',
    'NOT_IMPORTANT',
    '1_13',
    '13',
    '{}',
    false,
    'now()',
    'now()',
    'now()'
);
