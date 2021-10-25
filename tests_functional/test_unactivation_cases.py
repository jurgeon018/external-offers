import asyncio
from cian_json import json 
from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_functional_test_utils.data_fixtures import load_json_data


async def _create_test_objects(
    *,
    runtime_settings,
    http,
    pg,
):
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

    client_response = await http.request(
        'POST',
        '/api/admin/v1/create-test-client/',
        json=TEST_CLIENT_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    offer_response = await http.request(
        'POST',
        '/api/admin/v1/create-test-offer/',
        json=TEST_OFFER_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    client_id = json.loads(client_response.body.decode('utf-8'))['clientId']
    offer_id = json.loads(offer_response.body.decode('utf-8'))['offerId']
    return {
        'offer_id': offer_id,
        'client_id': client_id,
    }

async def _update_offers_list(
    *,
    http,
    users_mock,
    operator_id,
):
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={
                'roles': [
                    # {'id': 1, 'name': 'CommercialPrepublicationModerator'}
                ],
            }
        ),
    )
    response = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_id
        },
        json={},
        expected_status=200
    )    
    body = json.loads(response.body.decode('utf-8'))
    return body


async def test_main_case(
    pg,
    parsed_offers_fixture_for_unactivated_clients,
    runner,
    runtime_settings,
    users_mock,
    http,
    save_offer_request_body_with_create_new_account,
    queue_service,
    monolith_cian_announcementapi_mock,
    monolith_cian_service_mock,
    monolith_cian_profileapi_mock,
):
    offer_cian_id = 227888824
    sql = '''
        select * from offers_for_call
        join clients on clients.client_id = offers_for_call.client_id
        ;
    '''

    create_test_objects_result = await _create_test_objects()
    client_id = create_test_objects_result['client_id']
    offer_id = create_test_objects_result['offer_id']
    print()
    print('\nсозданы тестовые обьекты: ', await pg.fetch(sql))   

    # получить задания через админку
    update_offers_list_result = _update_offers_list()
    assert update_offers_list_result['status'] is True
    assert update_offers_list_result['errors'] == []
   
    print()
    print('получить задания через админку', await pg.fetch(sql))   
    print()
    # предразместить задание через админку
    # status='draft', publication_status=null
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': offer_cian_id,
                    'isAgent': True,
                }
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'countryId': 1233,
                'locationPath': [1],
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='POST',
        path='/v2/announcements/draft/',
        response=MockResponse(
            body={
                'realtyObjectId': 1243433,
            }
        ),
    )
    await monolith_cian_service_mock.add_stub(
        method='POST',
        path='/api/promocodes/create-promocode-group',
        response=MockResponse(
            status=400
        ),
    )
    await monolith_cian_profileapi_mock.add_stub(
        method='POST',
        path='/promocode/apply/',
        response=MockResponse(
            status=400
        ),
    )
    resp = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body_with_create_new_account,
        headers={
            'X-Real-UserId': operator_id
        }
    )
    print(resp)
    # await pg.fetchrow(f"""UPDATE offers_for_call SET offer_cian_id={offer_cian_id};""")
    print()
    print('предразместить задание через админку', await pg.fetch(sql))   
    print()
    offer = {
        "model": {
            "bargainTerms": {
            "price": 3103560.0
            },
            "phones": [
            {
                "number": "4012658894",
                "countryCode": "+7",
                "sourcePhone": {
                "number": "4012751166",
                "countryCode": "+7"
                }
            }
            ],
            "id": offer_cian_id,
            "cianId": offer_cian_id,
            "category": "newBuildingFlatSale",
            "rowVersion": 33324598804,
            "status": "Draft"
        },
        "operationId": "1934fc2a-7a72-494c-b050-dc38adc24ac6",
        "date": "2020-04-15T16:35:36.2632391+03:00"
    }
    # получить задания и увидеть "Отсутствуют доступные задания"(потому что клиент не стал еще добивочным)
    # обновить статус публикации(сделать клиента добивочным)
    # взять задания в работу, получить добивочного клиента в работу
    # вернуть добивочного клиента в перезвон
    # получить задание
    # вернуть добивочного клиента в перезвон
    # получить задание
    # вернуть добивочного клиента в перезвон
    # создать новое задание
    # получить задания
    return

    # arrange
    offer = {
        "model": {
            "bargainTerms": {
            "price": 3103560.0
            },
            "phones": [
            {
                "number": "4012658894",
                "countryCode": "+7",
                "sourcePhone": {
                "number": "4012751166",
                "countryCode": "+7"
                }
            }
            ],
            "id": 227888824,
            "cianId": 227888824,
            "category": "newBuildingFlatSale",
            "rowVersion": 33324598804,
            "status": "Draft"
        },
        "operationId": "1934fc2a-7a72-494c-b050-dc38adc24ac6",
        "date": "2020-04-15T16:35:36.2632391+03:00"
    }

    # offer = load_json_data(file, 'announcement_draft.json')
    operator_id = 1
    client_id = '86622a21-f502-4757-b5ae-fb40a2b312e0'
    offer_cian_id = offer['model']['id']
    save_offer_request_body_with_create_new_account['offerId'] = '6fd5ca86-0c66-4092-9c9e-967c66509931'
    save_offer_request_body_with_create_new_account['clientId'] = client_id
    # 0. Парсер присылает спаршеные обьявления
    await pg.execute_scripts(parsed_offers_fixture_for_unactivated_clients)

    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    # 1. срабатывает крон и создает из спаршеных обьявлений задания
    await runner.run_python_command('create-offers-for-call')

    # 2. оператор получает задание в работу
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={
                'roles': [
                    # {'id': 1, 'name': 'CommercialPrepublicationModerator'}
                ],
            }
        ),
    )
    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_id
        },
        json={},
        expected_status=200
    )

    # 3. оператор предразмещает обьявление клиента
    # status='draft', publication_status=null
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': offer_cian_id,
                    'isAgent': True,
                }
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'countryId': 1233,
                'locationPath': [1],
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='POST',
        path='/v2/announcements/draft/',
        response=MockResponse(
            body={
                'realtyObjectId': 1243433,
            }
        ),
    )
    await monolith_cian_service_mock.add_stub(
        method='POST',
        path='/api/promocodes/create-promocode-group',
        response=MockResponse(
            status=400
        ),
    )
    await monolith_cian_profileapi_mock.add_stub(
        method='POST',
        path='/promocode/apply/',
        response=MockResponse(
            status=400
        ),
    )
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body_with_create_new_account,
        headers={
            'X-Real-UserId': operator_id
        }
    )
    await pg.fetchrow(f"""UPDATE offers_for_call SET offer_cian_id={offer_cian_id};""")

    # 4. обьявление с обновленным статусом публикации приходит в консьюмер, 
    # publication_status='Draft'
    await queue_service.wait_consumer('external-offers.process_announcement_v2')
    await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
    await asyncio.sleep(1)

    # 5. повторно запускается крон
    # (гипотеза: тут удаляется черновик, который не должен удаляться)
    await runner.run_python_command('create-offers-for-call')

    # 6. убедиться что обьявление не удалилось
    offer_for_call_after = await pg.fetchrow(f"""
        SELECT * FROM offers_for_call WHERE offer_cian_id={offer_cian_id};
    """)
    client_after = await pg.fetchrow(f"""
        SELECT * FROM clients WHERE avito_user_id='c42bb598767308327e1dffbe7241486c';
    """)
    assert offer_for_call_after is not None
    assert client_after is not None




import asyncio

from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_unactivated_objects_deletion(
    pg,
    parsed_offers_fixture_for_unactivated_clients,
    runner,
    runtime_settings,
    users_mock,
    http,
    save_offer_request_body_with_create_new_account,
    queue_service,
    monolith_cian_announcementapi_mock,
    monolith_cian_service_mock,
    monolith_cian_profileapi_mock,
):
    # arrange
    offer = {
        "model": {
            "bargainTerms": {
            "price": 3103560.0
            },
            "phones": [
            {
                "number": "4012658894",
                "countryCode": "+7",
                "sourcePhone": {
                "number": "4012751166",
                "countryCode": "+7"
                }
            }
            ],
            "id": 227888824,
            "cianId": 227888824,
            "category": "newBuildingFlatSale",
            "rowVersion": 33324598804,
            "status": "Draft"
        },
        "operationId": "1934fc2a-7a72-494c-b050-dc38adc24ac6",
        "date": "2020-04-15T16:35:36.2632391+03:00"
    }

    # offer = load_json_data(__file__, 'announcement_draft.json')
    operator_id = 1
    client_id = '86622a21-f502-4757-b5ae-fb40a2b312e0'
    offer_cian_id = offer['model']['id']
    save_offer_request_body_with_create_new_account['offerId'] = '6fd5ca86-0c66-4092-9c9e-967c66509931'
    save_offer_request_body_with_create_new_account['clientId'] = client_id
    # 0. Парсер присылает спаршеные обьявления
    await pg.execute_scripts(parsed_offers_fixture_for_unactivated_clients)

    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    # 1. срабатывает крон и создает из спаршеных обьявлений задания
    await runner.run_python_command('create-offers-for-call')

    # 2. оператор получает задание в работу
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={
                'roles': [
                    # {'id': 1, 'name': 'CommercialPrepublicationModerator'}
                ],
            }
        ),
    )
    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_id
        },
        json={},
        expected_status=200
    )    

    # 3. оператор предразмещает обьявление клиента
    # status='draft', publication_status=null
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': offer_cian_id,
                    'isAgent': True,
                }
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='GET',
        path='/v1/geo/geocode/',
        response=MockResponse(
            body={
                'countryId': 1233,
                'locationPath': [1],
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )
    await monolith_cian_announcementapi_mock.add_stub(
        method='POST',
        path='/v2/announcements/draft/',
        response=MockResponse(
            body={
                'realtyObjectId': 1243433,
            }
        ),
    )
    await monolith_cian_service_mock.add_stub(
        method='POST',
        path='/api/promocodes/create-promocode-group',
        response=MockResponse(
            status=400
        ),
    )
    await monolith_cian_profileapi_mock.add_stub(
        method='POST',
        path='/promocode/apply/',
        response=MockResponse(
            status=400
        ),
    )
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=save_offer_request_body_with_create_new_account,
        headers={
            'X-Real-UserId': operator_id
        }
    )
    await pg.fetchrow(f"""UPDATE offers_for_call SET offer_cian_id={offer_cian_id};""")

    # 4. обьявление с обновленным статусом публикации приходит в консьюмер, 
    # publication_status='Draft'
    await queue_service.wait_consumer('external-offers.process_announcement_v2')
    await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
    await asyncio.sleep(1)

    # 5. повторно запускается крон
    # (гипотеза: тут удаляется черновик, который не должен удаляться)
    await runner.run_python_command('create-offers-for-call')

    # 6. убедиться что обьявление не удалилось
    offer_for_call_after = await pg.fetchrow(f"""
        SELECT * FROM offers_for_call WHERE offer_cian_id={offer_cian_id};
    """)
    client_after = await pg.fetchrow(f"""
        SELECT * FROM clients WHERE avito_user_id='c42bb598767308327e1dffbe7241486c';
    """)
    assert offer_for_call_after is not None
    assert client_after is not None
