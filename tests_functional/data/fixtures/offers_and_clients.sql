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
    1,
    1,
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    2,
    2,
    1,
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    3,
    3,
    2,
    'cancelled',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    4,
    4,
    3,
    'waiting',
    '2020-10-10 04:05:06',
    '2020-10-12 04:05:06'
), (
    5,
    5,
    2,
    'waiting',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    6,
    6,
    4,
    'inProgress',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
), (
    7,
    7,
    4,
    'cancelled',
    '2020-10-12 04:05:06',
    '2020-10-12 04:05:06'
);