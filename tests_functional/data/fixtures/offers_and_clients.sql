INSERT INTO public.clients(
    client_id,
    avito_user_id,
    client_name,
    client_phone,
    client_email,
    operator_user_id,
    status
) VALUES (
    1,
    32131322,
    'Александр Александров',
    '+79812333234',
    'testemail@gmail.com',
    60024635,
    'waiting'
), (
    2,
    32131323,
    'Александр Иванов',
    '+79812333235',
    'moyemail@gmail.com',
    NULL,
    'waiting'
), (
    3,
    32131324,
    'Александр Петров',
    '+79812333236',
    'nemoyemail@gmail.com',
    NULL,
    'waiting'
), (
    4,
    32131325,
    'Александр Петров',
    '+79812333237',
    'nemoyemail1234@gmail.com',
    60024638,
    'waiting'
);

INSERT INTO public.offers_for_call(
    id,
    parsed_id,
    client_id,
    status,
    created_at,
    started_at
) VALUES (
    1,
    'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
    1,
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    2,
    'f1a91ade-13a2-48d9-a05a-6131af39033e',
    1,
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    3,
    'fbd30a97-7bed-4459-8cfd-8ba797ac9054',
    2,
    'cancelled',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    4,
    '9999d421-b7ba-4ee0-b29f-bc8add87c933',
    3,
    'waiting',
    '2020-10-10 04:05:06',
    '2020-10-12 04:05:06'
), (
    5,
    '33e4d51e-e8d3-499d-9497-4229d6c539ee',
    2,
    'waiting',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    6,
    'wrong-parsed-id',
    4,
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    7,
    '1d6c73b8-3057-47cc-b50a-419052da619f',
    4,
    'cancelled',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
);