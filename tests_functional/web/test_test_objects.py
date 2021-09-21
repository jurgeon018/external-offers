import json

from cian_functional_test_utils.data_fixtures import load_json_data


async def test_create_offer_from_default_settings(
    http,
    pg,
    runtime_settings,
):
    # arrange
    use_default = True
    operator_id = '11111111'
    source_user_id = '12345'
    source_object_id = '1_356645'

    test_objects = load_json_data(__file__, 'test_objects.json')

    DEFAULT_TEST_OFFER = test_objects['DEFAULT_TEST_OFFER']
    DEFAULT_TEST_CLIENT = test_objects['DEFAULT_TEST_CLIENT']

    await runtime_settings.set({
        'DEFAULT_TEST_CLIENT': json.dumps(DEFAULT_TEST_CLIENT),
        'DEFULT_TEST_OFFER': json.dumps(DEFAULT_TEST_OFFER),
    })

    TEST_CLIENT_REQUEST = {}
    TEST_CLIENT_REQUEST['useDefault'] = use_default
    TEST_CLIENT_REQUEST['sourceUserId'] = source_user_id

    TEST_OFFER_REQUEST = {}
    TEST_OFFER_REQUEST['useDefault'] = use_default
    TEST_OFFER_REQUEST['sourceObjectId'] = source_object_id
    TEST_OFFER_REQUEST['sourceUserId'] = source_user_id

    # act
    client_response = await http.request(
        'POST',
        '/api/admin/v1/create-test-client/',
        json=TEST_CLIENT_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    client_id = json.loads(client_response.body.decode('utf-8'))['clientId']
    offer_response = await http.request(
        'POST',
        '/api/admin/v1/create-test-offer/',
        json=TEST_OFFER_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    offers_for_call_count = await pg.fetchval('SELECT COUNT(*) FROM offers_for_call;')
    offers_for_call = await pg.fetchrow('SELECT * FROM offers_for_call LIMIT 1;')
    parsed_offers_count = await pg.fetchval('SELECT COUNT(*) FROM parsed_offers;')
    parsed_offer = await pg.fetchrow('SELECT * FROM parsed_offers LIMIT 1;')
    resp = json.loads(offer_response.body.decode('utf-8'))

    assert resp['message'] == 'Тестовое обьявление было успешно создано.'
    assert resp['success'] is True
    assert offers_for_call_count == 1
    assert parsed_offers_count == 1
    assert offers_for_call['client_id'] == client_id

    assert offers_for_call['parsed_id'] == parsed_offer['id']
    assert offers_for_call['category'] == DEFAULT_TEST_OFFER['category']
    assert offers_for_call['offer_cian_id'] == DEFAULT_TEST_OFFER['offer_cian_id']
    assert offers_for_call['priority'] == DEFAULT_TEST_OFFER['offer_priority']

    assert parsed_offer['source_object_id'] == source_object_id
    assert parsed_offer['source_user_id'] == source_user_id
    assert parsed_offer['is_calltracking'] == DEFAULT_TEST_OFFER['is_calltracking']
    assert parsed_offer['user_segment'] == DEFAULT_TEST_OFFER['user_segment']

    source_object_model = json.loads(parsed_offer['source_object_model'])
    assert source_object_model['lat'] == DEFAULT_TEST_OFFER['lat']
    assert source_object_model['lng'] == DEFAULT_TEST_OFFER['lng']
    assert source_object_model['url'] == DEFAULT_TEST_OFFER['url']
    assert source_object_model['town'] == DEFAULT_TEST_OFFER['town']
    assert source_object_model['price'] == DEFAULT_TEST_OFFER['price']
    assert source_object_model['title'] == DEFAULT_TEST_OFFER['title']
    assert source_object_model['phones'] == [DEFAULT_TEST_OFFER['phone']]
    assert source_object_model['region'] == DEFAULT_TEST_OFFER['region']
    assert source_object_model['address'] == DEFAULT_TEST_OFFER['address']
    assert source_object_model['contact'] == DEFAULT_TEST_OFFER['contact']
    assert source_object_model['category'] == DEFAULT_TEST_OFFER['category']
    assert source_object_model['is_agency'] == DEFAULT_TEST_OFFER['is_agency']
    assert source_object_model['is_studio'] == DEFAULT_TEST_OFFER['is_studio']
    assert source_object_model['price_type'] == DEFAULT_TEST_OFFER['price_type']
    assert source_object_model['total_area'] == DEFAULT_TEST_OFFER['total_area']
    assert source_object_model['living_area'] == DEFAULT_TEST_OFFER['living_area']
    assert source_object_model['rooms_count'] == DEFAULT_TEST_OFFER['rooms_count']
    assert source_object_model['description'] == DEFAULT_TEST_OFFER['description']
    assert source_object_model['floor_number'] == DEFAULT_TEST_OFFER['floor_number']
    assert source_object_model['floors_count'] == DEFAULT_TEST_OFFER['floors_count']
    assert source_object_model['is_developer'] == DEFAULT_TEST_OFFER['is_developer']


async def test_create_offer_from_request_parameters(
    http,
    pg,
):
    # arrange
    use_default = False
    operator_id = '11111111'
    source_user_id = '12345'
    source_object_id = '1_356645'

    test_objects = load_json_data(__file__, 'test_objects.json')

    TEST_CLIENT_REQUEST = test_objects['TEST_CLIENT_REQUEST']
    TEST_CLIENT_REQUEST['useDefault'] = use_default
    TEST_CLIENT_REQUEST['sourceUserId'] = source_user_id

    TEST_OFFER_REQUEST = test_objects['TEST_OFFER_REQUEST']
    TEST_OFFER_REQUEST['useDefault'] = use_default
    TEST_OFFER_REQUEST['sourceObjectId'] = source_object_id
    TEST_OFFER_REQUEST['sourceUserId'] = source_user_id

    # act
    client_response = await http.request(
        'POST',
        '/api/admin/v1/create-test-client/',
        json=TEST_CLIENT_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    client_id = json.loads(client_response.body.decode('utf-8'))['clientId']
    offer_response = await http.request(
        'POST',
        '/api/admin/v1/create-test-offer/',
        json=TEST_OFFER_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    offers_for_call_count = await pg.fetchval('SELECT COUNT(*) FROM offers_for_call;')
    offers_for_call = await pg.fetchrow('SELECT * FROM offers_for_call LIMIT 1;')
    parsed_offers_count = await pg.fetchval('SELECT COUNT(*) FROM parsed_offers;')
    parsed_offer = await pg.fetchrow('SELECT * FROM parsed_offers LIMIT 1;')
    resp = json.loads(offer_response.body.decode('utf-8'))

    # assert
    assert resp['message'] == 'Тестовое обьявление было успешно создано.'
    assert resp['success'] is True
    assert offers_for_call_count == 1
    assert parsed_offers_count == 1
    assert offers_for_call['client_id'] == client_id

    assert offers_for_call['parsed_id'] == parsed_offer['id']
    assert offers_for_call['category'] == TEST_OFFER_REQUEST['category']
    assert offers_for_call['offer_cian_id'] == TEST_OFFER_REQUEST['offerCianId']
    assert offers_for_call['priority'] == TEST_OFFER_REQUEST['offerPriority']

    assert parsed_offer['source_object_id'] == source_object_id
    assert parsed_offer['source_user_id'] == source_user_id
    assert parsed_offer['is_calltracking'] == TEST_OFFER_REQUEST['isCalltracking']
    assert parsed_offer['user_segment'] == TEST_OFFER_REQUEST['userSegment']

    source_object_model = json.loads(parsed_offer['source_object_model'])
    assert source_object_model['lat'] == TEST_OFFER_REQUEST['lat']
    assert source_object_model['lng'] == TEST_OFFER_REQUEST['lng']
    assert source_object_model['url'] == TEST_OFFER_REQUEST['url']
    assert source_object_model['town'] == TEST_OFFER_REQUEST['town']
    assert source_object_model['price'] == TEST_OFFER_REQUEST['price']
    assert source_object_model['title'] == TEST_OFFER_REQUEST['title']
    assert source_object_model['phones'] == [TEST_OFFER_REQUEST['phone']]
    assert source_object_model['region'] == TEST_OFFER_REQUEST['region']
    assert source_object_model['address'] == TEST_OFFER_REQUEST['address']
    assert source_object_model['contact'] == TEST_OFFER_REQUEST['contact']
    assert source_object_model['category'] == TEST_OFFER_REQUEST['category']
    assert source_object_model['is_agency'] == TEST_OFFER_REQUEST['isAgency']
    assert source_object_model['is_studio'] == TEST_OFFER_REQUEST['isStudio']
    assert source_object_model['price_type'] == TEST_OFFER_REQUEST['priceType']
    assert source_object_model['total_area'] == TEST_OFFER_REQUEST['totalArea']
    assert source_object_model['living_area'] == TEST_OFFER_REQUEST['livingArea']
    assert source_object_model['rooms_count'] == TEST_OFFER_REQUEST['roomsCount']
    assert source_object_model['description'] == TEST_OFFER_REQUEST['description']
    assert source_object_model['floor_number'] == TEST_OFFER_REQUEST['floorNumber']
    assert source_object_model['floors_count'] == TEST_OFFER_REQUEST['floorsCount']
    assert source_object_model['is_developer'] == TEST_OFFER_REQUEST['isDeveloper']


async def test_create_client_from_default_settings(
    http,
    pg,
    runtime_settings,
):
    # arrange
    operator_id = '11111111'
    use_default = True
    source_user_id = '123123123'
    test_objects = load_json_data(__file__, 'test_objects.json')
    DEFAULT_TEST_CLIENT = test_objects['DEFAULT_TEST_CLIENT']
    await runtime_settings.set({
        'DEFAULT_TEST_CLIENT': json.dumps(DEFAULT_TEST_CLIENT),
    })
    TEST_CLIENT_REQUEST = {}
    TEST_CLIENT_REQUEST['useDefault'] = use_default
    TEST_CLIENT_REQUEST['sourceUserId'] = source_user_id

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/create-test-client/',
        json=TEST_CLIENT_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    clients_count = await pg.fetchval('SELECT COUNT(*) FROM clients;')
    client = await pg.fetchrow('SELECT * FROM clients LIMIT 1;')

    # assert
    resp = json.loads(response.body.decode('utf-8'))
    assert resp['success'] is True
    assert resp['message'] == 'Тестовый клиент был успешно создан.'
    assert clients_count == 1
    assert client['avito_user_id'] == source_user_id
    assert client['client_phones'] == [DEFAULT_TEST_CLIENT['client_phone'], ]
    assert client['client_name'] == DEFAULT_TEST_CLIENT['client_name']
    assert client['cian_user_id'] == DEFAULT_TEST_CLIENT['cian_user_id']
    assert client['client_email'] == DEFAULT_TEST_CLIENT['client_email']
    assert client['segment'] == DEFAULT_TEST_CLIENT['segment']
    assert client['main_account_chosen'] == DEFAULT_TEST_CLIENT['main_account_chosen']
    assert client['is_test'] is True
    assert client['status'] == 'waiting'
    assert client['operator_user_id'] is None
    assert client['last_call_id'] is None
    assert client['calls_count'] == 0
    assert client['next_call'] is None


async def test_create_client_from_request_parameters(
    http,
    pg,
):
    # arrange
    operator_id = '11111111'
    use_default = False
    source_user_id = '123123123'
    test_objects = load_json_data(__file__, 'test_objects.json')
    TEST_CLIENT_REQUEST = test_objects['TEST_CLIENT_REQUEST']
    TEST_CLIENT_REQUEST['useDefault'] = use_default
    TEST_CLIENT_REQUEST['sourceUserId'] = source_user_id

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/create-test-client/',
        json=TEST_CLIENT_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    clients_count = await pg.fetchval('SELECT COUNT(*) FROM clients;')
    client = await pg.fetchrow('SELECT * FROM clients LIMIT 1;')

    # assert
    resp = json.loads(response.body.decode('utf-8'))
    assert resp['success'] is True
    assert resp['message'] == 'Тестовый клиент был успешно создан.'
    assert clients_count == 1
    assert client['avito_user_id'] == source_user_id
    assert client['client_phones'] == [TEST_CLIENT_REQUEST['clientPhone'], ]
    assert client['client_name'] == TEST_CLIENT_REQUEST['clientName']
    assert client['cian_user_id'] == TEST_CLIENT_REQUEST['cianUserId']
    assert client['client_email'] == TEST_CLIENT_REQUEST['clientEmail']
    assert client['segment'] == TEST_CLIENT_REQUEST['segment']
    assert client['main_account_chosen'] == TEST_CLIENT_REQUEST['mainAccountChosen']
    assert client['is_test'] is True
    assert client['status'] == 'waiting'
    assert client['operator_user_id'] is None
    assert client['last_call_id'] is None
    assert client['calls_count'] == 0
    assert client['next_call'] is None


async def test_delete_test_objects(
    pg,
    http,
    offers_and_clients_fixture,
    parsed_offers_fixture,
    test_objects_fixture,
):
    # arrange
    operator_id = '11111111'
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    await pg.execute_scripts(test_objects_fixture)
    real_offers_before_api_call = await pg.fetchval('SELECT COUNT(*) FROM offers_for_call WHERE is_test IS FALSE')
    real_parsed_offers_before_api_call = await pg.fetchval('SELECT COUNT(*) FROM parsed_offers WHERE is_test IS FALSE')
    real_clients_before_api_call = await pg.fetchval('SELECT COUNT(*) FROM clients WHERE is_test IS FALSE')
    test_offers_before_api_call = await pg.fetchval('SELECT COUNT(*) FROM offers_for_call WHERE is_test IS TRUE')
    test_parsed_offers_before_api_call = await pg.fetchval('SELECT COUNT(*) FROM parsed_offers WHERE is_test IS TRUE')
    test_clients_before_api_call = await pg.fetchval('SELECT COUNT(*) FROM clients WHERE is_test IS TRUE')
    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/delete-test-objects/',
        json={},
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    resp = json.loads(response.body.decode('utf-8'))
    # assert

    real_offers_after_api_call = await pg.fetchval(
        'SELECT COUNT(*) FROM offers_for_call WHERE is_test IS FALSE'
    )
    real_parsed_offers_after_api_call = await pg.fetchval(
        'SELECT COUNT(*) FROM parsed_offers WHERE is_test IS FALSE'
    )
    real_clients_after_api_call = await pg.fetchval(
        'SELECT COUNT(*) FROM clients WHERE is_test IS FALSE'
    )
    test_offers_after_api_call = await pg.fetchval(
        'SELECT COUNT(*) FROM offers_for_call WHERE is_test IS TRUE'
    )
    test_parsed_offers_after_api_call = await pg.fetchval(
        'SELECT COUNT(*) FROM parsed_offers WHERE is_test IS TRUE'
    )
    test_clients_after_api_call = await pg.fetchval(
        'SELECT COUNT(*) FROM clients WHERE is_test IS TRUE'
    )
    assert resp['success'] is True
    assert resp['message'] == 'Тестовые обьекты были успешно удалены.'
    assert real_offers_after_api_call == real_offers_before_api_call
    assert real_parsed_offers_after_api_call == real_parsed_offers_before_api_call
    assert real_clients_after_api_call == real_clients_before_api_call
    assert test_offers_after_api_call == 0
    assert test_parsed_offers_after_api_call == 0
    assert test_clients_after_api_call == 0
    assert test_offers_before_api_call != 0
    assert test_parsed_offers_before_api_call != 0
    assert test_clients_before_api_call != 0


async def test_update_test_object_publication_status__offer_doesnt_exists__success_is_false(
    http,
    pg,
    runtime_settings,
):
    # arrange
    non_existing_offer_cian_id = 1
    # act
    update_response = await http.request(
        'POST',
        '/api/admin/v1/update-test-object-publication-status/',
        json={
            'offerCianId': non_existing_offer_cian_id,
            'rowVersion': 3,
            'publicationStatus': 'Draft',
        },
        headers={
            'X-Real-UserId': '1'
        },
        expected_status=200
    )
    resp = json.loads(update_response.body.decode('utf-8'))
    # assert
    assert resp['success'] is False
    assert resp['message'] == f'Обьявление с offer_cian_id {non_existing_offer_cian_id} не существует.'


async def test_update_test_object_publication_status__offer_is_not_test__success_is_false(
    http,
    pg,
):
    # arrange
    # Создается нетестовое задание
    offer_cian_id = 10
    await pg.execute(f"""
    INSERT INTO public.offers_for_call (
        is_test, offer_cian_id, id, parsed_id, client_id, status, created_at, synced_at
    ) VALUES (
        'f', {offer_cian_id}, 1, 1, 1, 'waiting', 'now()', 'now()'
    );
    """)
    operator_id = '11111111'
    publication_status = 'Draft'

    # act
    update_response = await http.request(
        'POST',
        '/api/admin/v1/update-test-object-publication-status/',
        json={
            'offerCianId': offer_cian_id,
            'rowVersion': 3,
            'publicationStatus': publication_status,
        },
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    resp = json.loads(update_response.body.decode('utf-8'))
    # assert
    assert resp['success'] is False
    assert resp['message'] == f'Обьявление с offer_cian_id {offer_cian_id} не тестовое.'


async def test_update_test_object_publication_status__invalid_row_version__success_is_false(
    http,
    pg,
    runtime_settings,
):
    # arrange
    row_version = -1
    use_default = False
    operator_id = '11111111'
    source_user_id = '12345'
    source_object_id = '1_356645'
    publication_status = 'Draft'

    test_objects = load_json_data(__file__, 'test_objects.json')

    TEST_CLIENT_REQUEST = test_objects['TEST_CLIENT_REQUEST']
    TEST_CLIENT_REQUEST['useDefault'] = use_default
    TEST_CLIENT_REQUEST['sourceUserId'] = source_user_id

    TEST_OFFER_REQUEST = test_objects['TEST_OFFER_REQUEST']
    TEST_OFFER_REQUEST['useDefault'] = use_default
    TEST_OFFER_REQUEST['sourceObjectId'] = source_object_id
    TEST_OFFER_REQUEST['sourceUserId'] = source_user_id

    # act
    await http.request(
        'POST',
        '/api/admin/v1/create-test-client/',
        json=TEST_CLIENT_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    await http.request(
        'POST',
        '/api/admin/v1/create-test-offer/',
        json=TEST_OFFER_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    update_response = await http.request(
        'POST',
        '/api/admin/v1/update-test-object-publication-status/',
        json={
            'offerCianId': TEST_OFFER_REQUEST['offerCianId'],
            'rowVersion': row_version,
            'publicationStatus': publication_status,
        },
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    resp = json.loads(update_response.body.decode('utf-8'))
    # assert
    assert resp['success'] is False
    assert resp['message'] == 'new_version должен быть > 0'


async def test_update_test_object_publication_status__params_are_valid__success_is_true(
    http,
    pg,
    runtime_settings,
):
    # arrange
    use_default = False
    operator_id = '11111111'
    source_user_id = '12345'
    source_object_id = '1_356645'
    publication_status = 'Draft'

    test_objects = load_json_data(__file__, 'test_objects.json')

    TEST_CLIENT_REQUEST = test_objects['TEST_CLIENT_REQUEST']
    TEST_CLIENT_REQUEST['useDefault'] = use_default
    TEST_CLIENT_REQUEST['sourceUserId'] = source_user_id

    TEST_OFFER_REQUEST = test_objects['TEST_OFFER_REQUEST']
    TEST_OFFER_REQUEST['useDefault'] = use_default
    TEST_OFFER_REQUEST['sourceObjectId'] = source_object_id
    TEST_OFFER_REQUEST['sourceUserId'] = source_user_id

    # act
    await http.request(
        'POST',
        '/api/admin/v1/create-test-client/',
        json=TEST_CLIENT_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    await http.request(
        'POST',
        '/api/admin/v1/create-test-offer/',
        json=TEST_OFFER_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    update_response = await http.request(
        'POST',
        '/api/admin/v1/update-test-object-publication-status/',
        json={
            'offerCianId': TEST_OFFER_REQUEST['offerCianId'],
            'rowVersion': 3,
            'publicationStatus': publication_status,
        },
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    resp = json.loads(update_response.body.decode('utf-8'))
    # assert
    assert resp['message'] == f'Успех! Статус был изменен на {publication_status}.'
    assert resp['success'] is True
