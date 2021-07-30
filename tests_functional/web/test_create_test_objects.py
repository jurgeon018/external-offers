import json
import pytest 


TEST_OFFER = {
    # offers_for_call
    'offer_cian_id': None,
    'offer_priority': 1,
    # parsed_offers
    'parsed_id': 'ad49365b-caa3-4d8a-be58-02360ad338d5',
    'source_object_id': '1_1308836235',
    'source_user_id': '7960b9caba94ad3aa42a284d44d9fbfb',
    'is_calltracking': False,
    'user_segment': 'c',
    # source_object_model
    'lat': 55.799034118652344,
    'lng': 37.782142639160156,
    'url': 'https://www.avito.ru/moskva/komnaty/komnata_13_m_v_3-k_35_et._1308836235',
    'town': 'Москва',
    'price': 16000,
    'title': 'Комната 13 м² в 3-к, 3/5 эт.',
    'phone': "88005553535",
    'region': 1,
    'address': 'Москва, 3-я Парковая ул.',
    'contact': 'Тестовый клиент',
    'category': 'roomRent',
    'is_agency': 1,
    'is_studio': None,
    'price_type': 6,
    'total_area': 13,
    'living_area': None,
    'rooms_count': 4,
    'description': 'Рассмотрим всех!для проживания все необходимое имеется,тихие соседи,места общего пользования в обычном состоянии,национальность не принципиальна,срочно!в стоимость все включено,фото реальны,комната с балконом,залог есть минимальный',
    'floor_number': 3,
    'floors_count': 6,
    'is_developer': None
    # 'updateDate': '2021-07-16 15:42:00',
}
TEST_OFFER_REQUEST = {
    'offerCianId': TEST_OFFER['offer_cian_id'],
    'offerPriority': TEST_OFFER['offer_priority'],
    'parsedId': TEST_OFFER['parsed_id'],
    'sourceObjectId': TEST_OFFER['source_object_id'],
    'sourceUserId': TEST_OFFER['source_user_id'],
    'isCalltracking': TEST_OFFER['is_calltracking'],
    'userSegment': TEST_OFFER['user_segment'],
    'lat': TEST_OFFER['lat'],
    'lng': TEST_OFFER['lng'],
    'url': TEST_OFFER['url'],
    'town': TEST_OFFER['town'],
    'price': TEST_OFFER['price'],
    'title': TEST_OFFER['title'],
    'phone': TEST_OFFER['phone'],
    'region': TEST_OFFER['region'],
    'address': TEST_OFFER['address'],
    'contact': TEST_OFFER['contact'],
    'category': TEST_OFFER['category'],
    'isAgency': TEST_OFFER['is_agency'],
    'isStudio': TEST_OFFER['is_studio'],
    'priceType': TEST_OFFER['price_type'],
    'totalArea': TEST_OFFER['total_area'],
    'livingArea': TEST_OFFER['living_area'],
    'roomsCount': TEST_OFFER['rooms_count'],
    'description': TEST_OFFER['description'],
    'floorNumber': TEST_OFFER['floor_number'],
    'floorsCount': TEST_OFFER['floors_count'],
    'isDeveloper': TEST_OFFER['is_developer'],
}
TEST_CLIENT = {
    'avito_user_id': TEST_OFFER['source_user_id'],
    'segment':  TEST_OFFER['user_segment'],
    'client_phone': TEST_OFFER['phone'],
    'client_name': TEST_OFFER['contact'],
    'cian_user_id': None,
    'client_email': '111@21.11',
    'main_account_chosen': False,
}
TEST_CLIENT_REQUEST = {
    'avitoUserId': TEST_CLIENT['avito_user_id'],
    'segment': TEST_CLIENT['segment'],
    'clientPhone': TEST_CLIENT['client_phone'],
    'clientName': TEST_CLIENT['client_name'],
    'cianUserId': TEST_CLIENT['cian_user_id'],
    'clientEmail': TEST_CLIENT['client_email'],
    'mainAccountChosen': TEST_CLIENT['main_account_chosen'],
}

@pytest.mark.parametrize('use_default', [
    True,
    False
])
async def test_create_default_client(
    http,
    pg,
    runtime_settings,
    use_default,
):
    # arrange
    operator_id = '11111111'
    json_data = {
        'useDefault': use_default
    }
    if use_default is True:
        await runtime_settings.set({
            'DEFAULT_TEST_CLIENT': TEST_CLIENT,
        })
    elif use_default is False:
        await runtime_settings.set({
            'DEFAULT_TEST_CLIENT': None,
        })
        json_data.update(TEST_CLIENT_REQUEST)
    # act
   
    response = await http.request(
        'POST',
        '/api/admin/v1/create-test-client/',
        json=json_data,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    clients_count = await pg.fetchval("SELECT COUNT(*) FROM clients;")
    client = await pg.fetchrow("SELECT * FROM clients LIMIT 1;")
    # assert
    resp = json.loads(response.body.decode('utf-8'))
    assert resp['success'] is True
    assert resp['message'] == 'Тестовый клиент был успешно создан.'
    assert clients_count == 1
    assert client['avito_user_id'] == TEST_CLIENT['avito_user_id']
    assert client['client_phones'] == [TEST_CLIENT['client_phone'],]
    assert client['client_name'] == TEST_CLIENT['client_name']
    assert client['cian_user_id'] == TEST_CLIENT['cian_user_id']
    assert client['client_email'] == TEST_CLIENT['client_email']
    assert client['segment'] == TEST_CLIENT['segment']
    assert client['main_account_chosen'] == TEST_CLIENT['main_account_chosen']
    assert client['is_test'] == True
    assert client['status'] == 'waiting'
    assert client['operator_user_id'] == None
    assert client['last_call_id'] == None
    assert client['calls_count'] == 0
    assert client['next_call'] == None


@pytest.mark.parametrize('use_default', [
    True,
    False
    ])
async def test_create_default_offer(
    http,
    pg,
    runtime_settings,
    use_default,
):
    # arrange
    operator_id = '11111111'
    client_json_data = {
        'useDefault': use_default,
    }
    offer_json_data = {
        'useDefault': use_default,
    }
    if use_default:
        await runtime_settings.set({
            'DEFAULT_TEST_CLIENT': TEST_CLIENT,
            'DEFAULT_TEST_OFFER': TEST_OFFER,
        })
    else:
        await runtime_settings.set({
            'DEFAULT_TEST_CLIENT': None,
            'DEFAULT_TEST_OFFER': None,
        })
        client_json_data.update(TEST_CLIENT_REQUEST)
        offer_json_data.update(TEST_OFFER_REQUEST)
    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/create-test-client/',
        json=client_json_data,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    client_id = json.loads(response.body.decode('utf-8'))['clientId']
    offer_json_data['clientId'] = client_id
    response = await http.request(
        'POST',
        '/api/admin/v1/create-test-offer/',
        json=offer_json_data,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    offers_for_call_count = await pg.fetchval("SELECT COUNT(*) FROM offers_for_call;")
    offers_for_call = await pg.fetchrow("SELECT * FROM offers_for_call LIMIT 1;")
    parsed_offers_count = await pg.fetchval("SELECT COUNT(*) FROM parsed_offers;")
    parsed_offer = await pg.fetchrow("SELECT * FROM parsed_offers LIMIT 1;")
    resp = json.loads(response.body.decode('utf-8'))
    source_object_model = json.loads(parsed_offer['source_object_model'])

    # assert
    assert resp['success'] is True
    assert resp['message'] == 'Тестовое обьявление было успешно создано.'
    assert offers_for_call_count == 1
    assert parsed_offers_count == 1
    assert offers_for_call['client_id'] == client_id

    assert offers_for_call['parsed_id'] == TEST_OFFER['parsed_id']
    assert offers_for_call['category'] == TEST_OFFER['category']
    assert offers_for_call['offer_cian_id'] == TEST_OFFER['offer_cian_id']
    assert offers_for_call['priority'] == TEST_OFFER['offer_priority']

    assert parsed_offer['id'] == TEST_OFFER['parsed_id']
    assert parsed_offer['source_object_id'] == TEST_OFFER['source_object_id']
    assert parsed_offer['source_user_id'] == TEST_OFFER['source_user_id']
    assert parsed_offer['is_calltracking'] == TEST_OFFER['is_calltracking']
    assert parsed_offer['user_segment'] == TEST_OFFER['user_segment']

    assert source_object_model['lat'] == TEST_OFFER['lat']
    assert source_object_model['lng'] == TEST_OFFER['lng']
    assert source_object_model['url'] == TEST_OFFER['url']
    assert source_object_model['town'] == TEST_OFFER['town']
    assert source_object_model['price'] == TEST_OFFER['price']
    assert source_object_model['title'] == TEST_OFFER['title']
    assert source_object_model['phones'] == [TEST_OFFER['phone']]
    assert source_object_model['region'] == TEST_OFFER['region']
    assert source_object_model['address'] == TEST_OFFER['address']
    assert source_object_model['contact'] == TEST_OFFER['contact']
    assert source_object_model['category'] == TEST_OFFER['category']
    assert source_object_model['is_agency'] == TEST_OFFER['is_agency']
    assert source_object_model['is_studio'] == TEST_OFFER['is_studio']
    assert source_object_model['price_type'] == TEST_OFFER['price_type']
    assert source_object_model['total_area'] == TEST_OFFER['total_area']
    assert source_object_model['living_area'] == TEST_OFFER['living_area']
    assert source_object_model['rooms_count'] == TEST_OFFER['rooms_count']
    assert source_object_model['description'] == TEST_OFFER['description']
    assert source_object_model['floor_number'] == TEST_OFFER['floor_number']
    assert source_object_model['floors_count'] == TEST_OFFER['floors_count']
    assert source_object_model['is_developer'] == TEST_OFFER['is_developer']
