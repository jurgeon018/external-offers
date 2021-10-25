import asyncio
from datetime import datetime, timedelta

import pytz
from cian_functional_test_utils.data_fixtures import load_json_data
from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


async def test_main_case(
    pg,
    parsed_offers_fixture_for_unactivated_clients,
    runner,
    save_offer_request_body_with_create_new_account,
    runtime_settings,
    users_mock,
    http,
    queue_service,
    monolith_cian_announcementapi_mock,
    monolith_cian_service_mock,
    monolith_cian_profileapi_mock,
):
    fetch_ofc_sql = 'select * from offers_for_call;'
    fetch_clients_sql = 'select * from clients;'
    operator_id = 11111111
    source_user_id = '1'
    source_object_id = '1_1'
    source_object_id2 = '1_2'
    offer_cian_id = 227888824
    cian_user_id = 1232132323
    new_row_version = 33324598804

    # # # # # тест cтандартного кейса админки
    # print()
    # print('создать тестовые задания и тестовых клиентов')
    client_id = await _create_test_client(
        runtime_settings=runtime_settings,
        http=http,
        operator_id=operator_id,
        source_user_id=source_user_id
    )
    offer_id = await _create_test_offer(
        runtime_settings=runtime_settings,
        http=http,
        operator_id=operator_id,
        source_user_id=source_user_id,
        source_object_id=source_object_id,
    )
    ofc = await pg.fetch(fetch_ofc_sql)
    clients = await pg.fetch(fetch_clients_sql)
    # _print(ofc=ofc[0], client=clients[0])
    assert len(ofc) == 1
    assert len(clients) == 1
    assert ofc[0]['status'] == 'waiting'
    assert ofc[0]['client_id'] == client_id
    assert ofc[0]['row_version'] == 0
    assert ofc[0]['is_test'] is True
    assert ofc[0]['id'] == offer_id
    assert ofc[0]['status'] == 'waiting'
    assert clients[0]['status'] == 'waiting'
    assert clients[0]['client_id'] == client_id
    assert clients[0]['operator_user_id'] is None
    assert clients[0]['unactivated'] is False
    assert clients[0]['avito_user_id'] == source_user_id
    assert clients[0]['is_test'] is True

    # # # #
    # print()
    # print('получить задания через админку первый раз после создания заданий')
    update_offers_list_response = await _update_offers_list(
        http=http,
        users_mock=users_mock,
        operator_id=operator_id,
    )
    ofc = await pg.fetch(fetch_ofc_sql)
    clients = await pg.fetch(fetch_clients_sql)
    # _print(ofc=ofc[0], client=clients[0])
    assert update_offers_list_response['success'] is True
    assert update_offers_list_response['errors'] == []
    assert len(ofc) == 1
    assert len(clients) == 1
    assert ofc[0]['status'] == 'inProgress'
    assert ofc[0]['row_version'] == 0
    assert ofc[0]['client_id'] == client_id
    assert ofc[0]['id'] == offer_id
    assert clients[0]['operator_user_id'] == operator_id
    assert clients[0]['client_id'] == client_id
    assert clients[0]['status'] == 'inProgress'

    # # # # #
    # print()
    # print('предразместить задание через админку')
    save_offer_response = await _save_offer(
        http=http,
        offer_id=offer_id,
        client_id=client_id,
        users_mock=users_mock,
        promocode_name='promocode1',
        cian_user_id=cian_user_id,
        monolith_cian_announcementapi_mock=monolith_cian_announcementapi_mock,
        monolith_cian_service_mock=monolith_cian_service_mock,
        monolith_cian_profileapi_mock=monolith_cian_profileapi_mock,
        offer_cian_id=offer_cian_id,
        operator_id=operator_id,
    )
    ofc = await pg.fetch(fetch_ofc_sql)
    clients = await pg.fetch(fetch_clients_sql)
    # _print(ofc=ofc[0], client=clients[0])
    assert save_offer_response['status'] == 'ok'
    assert save_offer_response['message'] == 'Объявление успешно создано'
    assert clients[0]['status'] == 'accepted'
    assert clients[0]['unactivated'] is False
    assert clients[0]['next_call'] is None
    assert ofc[0]['row_version'] == 0
    assert ofc[0]['status'] == 'draft'
    assert ofc[0]['publication_status'] is None
    assert ofc[0]['offer_cian_id'] == offer_cian_id

    # # # # #
    # print()
    # print('взять задания после предразмещения клиент не стал еще добивочным)')
    update_offers_list_response = await _update_offers_list(
        http=http,
        users_mock=users_mock,
        operator_id=operator_id,
    )
    ofc = await pg.fetch(fetch_ofc_sql)
    clients = await pg.fetch(fetch_clients_sql)
    # _print(ofc=ofc[0], client=clients[0])
    assert update_offers_list_response['success'] is False
    assert update_offers_list_response['errors'][0]['message'] == 'Отсутствуют доступные задания'
    assert update_offers_list_response['errors'][0]['code'] == 'suitableClientMissing'
    assert ofc[0]['status'] == 'draft'
    assert ofc[0]['row_version'] == 0
    assert clients[0]['operator_user_id'] == operator_id
    assert clients[0]['status'] == 'accepted'
    assert clients[0]['unactivated'] is False

    # # # # #
    # print()
    # print('обновить статус публикации(сделать клиента добивочным)')
    # await _update_publication_status(
    #     queue_service=queue_service,
    #     offer_cian_id=offer_cian_id,
    #     cian_user_id=cian_user_id,
    #     new_row_version=new_row_version,
    # )
    response = await _update_test_object_publication_status(
        http=http,
        operator_id=operator_id,
        offer_cian_id=offer_cian_id,
        row_version=new_row_version,
        publication_status='Draft',
    )

    ofc = await pg.fetch(fetch_ofc_sql)
    clients = await pg.fetch(fetch_clients_sql)
    # _print(ofc=ofc[0], client=clients[0])
    assert response['success'] is True
    assert response['message'] == 'Успех! Статус был изменен на Draft.'
    assert ofc[0]['publication_status'] == 'Draft'
    assert ofc[0]['row_version'] == new_row_version
    assert ofc[0]['status'] == 'draft'
    assert ofc[0]['offer_cian_id'] == offer_cian_id
    assert clients[0]['status'] == 'accepted'
    assert clients[0]['unactivated'] is True

    # # # # #
    # print()
    # print('взять задания в работу, получить добивочного клиента в работу.')
    # Нужно уменьшить дату для того чтобы сработала проверка
    # clients.c.next_call <= now в assign_suitable_client_to_operator
    next_call = (datetime.now(pytz.utc) - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')
    await pg.execute(f"""
        update clients set next_call = '{next_call}' where client_id = '{client_id}'
    """)
    update_offers_list_response = await _update_offers_list(
        http=http,
        users_mock=users_mock,
        operator_id=operator_id,
    )
    ofc = await pg.fetch(fetch_ofc_sql)
    clients = await pg.fetch(fetch_clients_sql)
    # _print(ofc=ofc[0], client=clients[0])
    assert update_offers_list_response['success'] is True
    assert update_offers_list_response['errors'] == []
    assert clients[0]['operator_user_id'] == operator_id
    assert clients[0]['status'] == 'inProgress'
    assert ofc[0]['status'] == 'inProgress'

    # # # # # cтандартный кейс админки закончился

    # # # # # тест добивочных карточек
    # print()
    # print('вернуть добивочного клиента в перезвон')
    dt = datetime.now(pytz.utc) - timedelta(days=4)
    call_later_datetime = (dt).strftime('%Y-%m-%d %H:%M:%S')
    _call_later_status_response = await _set_call_later_status_for_client(
        http=http,
        operator_id=operator_id,
        client_id=client_id,
        call_later_datetime=call_later_datetime,
    )
    ofc = await pg.fetch(fetch_ofc_sql)
    clients = await pg.fetch(fetch_clients_sql)
    # _print(ofc=ofc[0], client=clients[0])
    assert _call_later_status_response['success'] is True
    assert _call_later_status_response['errors'] == []
    assert clients[0]['operator_user_id'] == operator_id
    assert clients[0]['status'] == 'callLater'
    assert clients[0]['next_call'].date() == dt.date()
    assert ofc[0]['status'] == 'callLater'

    # # # # # #
    offer_id2 = await _create_test_offer(
        runtime_settings=runtime_settings,
        http=http,
        operator_id=operator_id,
        source_user_id=source_user_id,
        source_object_id=source_object_id2
    )
    ofc = await pg.fetch(fetch_ofc_sql)
    clients = await pg.fetch(fetch_clients_sql)
    # print('создать новое задание')
    # _print(ofc=ofc[0], client=clients[0])
    assert len(ofc) == 2
    assert len(clients) == 1
    assert clients[0]['status'] == 'callLater'
    assert ofc[0]['client_id'] == client_id
    assert ofc[0]['id'] == offer_id
    assert ofc[0]['status'] == 'callLater'
    assert ofc[1]['client_id'] == client_id
    assert ofc[1]['id'] == offer_id2
    assert ofc[1]['status'] == 'waiting'

    # # # # # #
    # print('получить задания')
    update_offers_list_response = await _update_offers_list(
        http=http,
        users_mock=users_mock,
        operator_id=operator_id,
    )
    ofc = await pg.fetch(fetch_ofc_sql)
    clients = await pg.fetch(fetch_clients_sql)
    # _print(ofc=ofc[0], client=clients[0])
    # _print(ofc=ofc[1])
    assert update_offers_list_response['success'] is True
    assert update_offers_list_response['errors'] == []
    assert clients[0]['status'] == 'inProgress'
    assert ofc[1]['status'] == 'inProgress'
    assert ofc[0]['status'] == 'inProgress'
    # # # # # тест добивочных карточек закончился


# def _print(*, ofc=None, client=None):
#     if ofc:
#         for key, value in ofc.items():
#            print('offers_for_call.{key: <22}{value}'.format(key=key, value=value))
#            print(key, value)
#     if client:
#         for key, value in client.items():
#            print('clients.{key: <30}{value}'.format(key=key, value=value))
#            print('key, value)


async def _create_test_client(
    *,
    runtime_settings,
    http,
    source_user_id,
    operator_id,
):
    test_objects = load_json_data(__file__, 'test_objects.json')
    TEST_CLIENT_REQUEST = {}
    TEST_CLIENT_REQUEST['useDefault'] = True
    TEST_CLIENT_REQUEST['sourceUserId'] = source_user_id
    DEFAULT_TEST_CLIENT = test_objects['DEFAULT_TEST_CLIENT']
    await runtime_settings.set({
        'DEFAULT_TEST_CLIENT': json.dumps(DEFAULT_TEST_CLIENT),
    })
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
    return client_id


async def _create_test_offer(
    *,
    runtime_settings,
    http,
    operator_id,
    source_user_id,
    source_object_id,
):
    test_objects = load_json_data(__file__, 'test_objects.json')
    TEST_OFFER_REQUEST = {}
    TEST_OFFER_REQUEST['useDefault'] = True
    TEST_OFFER_REQUEST['sourceObjectId'] = source_object_id
    TEST_OFFER_REQUEST['sourceUserId'] = source_user_id
    DEFAULT_TEST_OFFER = test_objects['DEFAULT_TEST_OFFER']
    await runtime_settings.set({
        'DEFULT_TEST_OFFER': json.dumps(DEFAULT_TEST_OFFER),
    })
    offer_response = await http.request(
        'POST',
        '/api/admin/v1/create-test-offer/',
        json=TEST_OFFER_REQUEST,
        headers={
            'X-Real-UserId': operator_id
        },
        expected_status=200
    )
    offer_id = json.loads(offer_response.body.decode('utf-8'))['offerId']
    return offer_id


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
        json={
            'isTest': True,
        },
        expected_status=200
    )
    response = json.loads(response.body.decode('utf-8'))
    return response


async def _save_offer(
    *,
    http,
    users_mock,
    monolith_cian_announcementapi_mock,
    monolith_cian_service_mock,
    monolith_cian_profileapi_mock,
    offer_id,
    client_id,
    offer_cian_id,
    cian_user_id,
    operator_id,
    promocode_name,
):
    # status='draft', publication_status=null
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )
    await users_mock.add_stub(
        method='POST',
        path='/v1/register-user-by-phone/',
        response=MockResponse(
            body={
                'hasManyAccounts': False,
                'isRegistered': True,
                'userData': {
                    'email': 'testemail@cian.ru',
                    'id': cian_user_id,
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
                'realtyObjectId': offer_cian_id,
            }
        ),
    )
    await monolith_cian_service_mock.add_stub(
        method='POST',
        path='/api/promocodes/create-promocode-group',
        response=MockResponse(
            status=200,
            body={
                'id': 1,
                'promocodes': [
                    {'promocode': promocode_name}
                ]
            }
        ),
    )
    await monolith_cian_profileapi_mock.add_stub(
        method='POST',
        path='/promocode/apply/',
        response=MockResponse(
            status=200,
            body=''
        ),
    )
    resp = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json={
            'createNewAccount': False,
            'dealType': 'sale',
            'offerType': 'suburban',
            'category': 'land',
            'address': 'ул. просторная 6, квартира 200',
            'realtyType': None,
            'totalArea': 120,
            'rooms_count': None,
            'floor_number': None,
            'floors_count': None,
            'price': 100000,
            'saleType': '',
            'offerId': offer_id,
            'clientId': client_id,
            'description': 'Test',
            'landArea': 6.0,
            'areaUnitType': 'sotka',
            'landStatus': 'individualHousingConstruction'
        },
        headers={
            'X-Real-UserId': operator_id
        }
    )
    response = json.loads(resp.body.decode('utf-8'))
    return response


async def _set_call_later_status_for_client(
    *,
    http,
    operator_id,
    client_id,
    call_later_datetime,
):
    response = await http.request(
        'POST',
        '/api/admin/v1/call-later-client/',
        headers={
            'X-Real-UserId': operator_id
        },
        json={
            'clientId': client_id,
            'callLaterDatetime': call_later_datetime,
        },
        expected_status=200
    )
    response = json.loads(response.body.decode('utf-8'))
    return response


async def _update_publication_status(
    *,
    offer_cian_id,
    cian_user_id,
    queue_service,
    new_row_version,
):
    offer = {
        'model': {
            'bargainTerms': {
                'price': 3103560.0
            },
            'phones': [
                {
                    'number': '4012658894',
                    'countryCode': '+7',
                    'sourcePhone': {
                        'number': '4012751166',
                        'countryCode': '+7'
                    }
                }
            ],
            'id': offer_cian_id,
            'userId': cian_user_id,
            'cianUserId': cian_user_id,
            'cianId': offer_cian_id,
            'category': 'newBuildingFlatSale',
            'rowVersion': new_row_version,
            'status': 'Draft'
        },
        'operationId': '1934fc2a-7a72-494c-b050-dc38adc24ac6',
        'date': '2020-04-15T16:35:36.2632391+03:00'
    }
    await queue_service.wait_consumer('external-offers.process_announcement_v2')
    await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
    await asyncio.sleep(1)


async def _update_test_object_publication_status(
    *,
    http,
    operator_id,
    offer_cian_id,
    row_version,
    publication_status,
):
    response = await http.request(
        'POST',
        '/api/admin/v1/update-test-object-publication-status/',
        headers={
            'X-Real-UserId': operator_id
        },
        json={
            'offerCianId': offer_cian_id,
            'rowVersion': row_version,
            'publicationStatus': publication_status,
        },
        expected_status=200
    )
    response = json.loads(response.body.decode('utf-8'))
    return response


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
        'model': {
            'bargainTerms': {
                'price': 3103560.0
            },
            'phones': [
                {
                    'number': '4012658894',
                    'countryCode': '+7',
                    'sourcePhone': {
                        'number': '4012751166',
                        'countryCode': '+7'
                    }
                }
            ],
            'id': 227888824,
            'cianId': 227888824,
            'category': 'newBuildingFlatSale',
            'rowVersion': 33324598804,
            'status': 'Draft'
        },
        'operationId': '1934fc2a-7a72-494c-b050-dc38adc24ac6',
        'date': '2020-04-15T16:35:36.2632391+03:00'
    }

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
    client_after = await pg.fetchrow("""
        SELECT * FROM clients WHERE avito_user_id='c42bb598767308327e1dffbe7241486c';
    """)
    assert offer_for_call_after is not None
    assert client_after is not None
