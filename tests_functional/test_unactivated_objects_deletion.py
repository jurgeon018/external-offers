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
    client_id = '52dbfb28-73a7-41c8-85b3-230c990ca57d'
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

    # 6. убедиться что обьявление удалилось
    offer_for_call_after = await pg.fetchrow(f"""
        SELECT * FROM offers_for_call WHERE offer_cian_id={offer_cian_id};
    """)
    client_after = await pg.fetchrow(f"""
        SELECT * FROM clients WHERE client_id='{client_id}';
    """)
    assert offer_for_call_after is None
    assert client_after is None