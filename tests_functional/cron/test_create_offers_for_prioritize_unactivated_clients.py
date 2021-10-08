from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_prioritize_unactivated_clients(
    pg,
    runtime_settings,
    users_mock,
    monolith_cian_profileapi_mock,
    announcements_mock,
    runner,
):
    # arrange
    # приоретизация обьявления 1 должна вернуть _CLEAR_CLIENT_PRIORITY, т.к у него нет сегмента
    priority_1 = 223456789
    priority_2 = "NULL"
    priority_3 = "NULL"
    priority_4 = "NULL"
    priority_5 = "NULL"
    # приоретизация обьявления 6 должна вернуть _CLEAR_CLIENT_PRIORITY, т.к у него нет региона
    priority_6 = 987654333
    await pg.execute("""
        INSERT INTO clients (
            segment, unactivated, client_id, avito_user_id, client_phones, status
        ) VALUES
        (NULL, 't', 1, 1, '{+7232121}', 'accepted'),
        ('c',  't', 2, 2, '{+7232122}', 'accepted'),
        ('d',  't', 3, 3, '{+7232123}', 'accepted'),
        ('d',  't', 4, 4, '{+7232123}', 'accepted');
    """)
    await pg.execute(f"""
        INSERT INTO offers_for_call (
            id, parsed_id, client_id, publication_status, status, category,   created_at, synced_at, priority
        ) VALUES
        (1, 1, 1, 'Draft', 'draft', 'flatRent', 'now()', 'now()', {priority_1}),
        (2, 2, 2, 'Draft', 'draft', 'flatRent', 'now()', 'now()', {priority_2}),
        (3, 3, 2, 'Draft', 'draft', 'flatRent', 'now()', 'now()', {priority_3}),
        (4, 4, 3, 'Draft', 'draft', 'flatRent', 'now()', 'now()', {priority_4}),
        (5, 5, 3, 'Draft', 'draft', 'flatRent', 'now()', 'now()', {priority_5}),
        (6, 6, 4, 'Draft', 'draft', 'flatRent', 'now()', 'now()', {priority_6});
    """)
    await pg.execute("""
        INSERT INTO parsed_offers (
            id, source_object_id, source_user_id,source_object_model,is_calltracking,timestamp,created_at,updated_at
        ) VALUES
        (1, 1, 1, '{\"region\": \"4568\"}',     'f', 'now()', 'now()', 'now()'),
        (2, 2, 2, '{\"region\": \"4636\"}',     'f', 'now()', 'now()', 'now()'),
        (3, 3, 2, '{\"region\": \"4624\"}',     'f', 'now()', 'now()', 'now()'),
        (4, 4, 3, '{\"region\": \"4568\"}',     'f', 'now()', 'now()', 'now()'),
        (5, 5, 3, '{\"region\": \"4636\"}',     'f', 'now()', 'now()', 'now()'),
        (6, 6, 4, '{}',                         'f', 'now()', 'now()', 'now()');
    """)

    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': [
            'flatSale', 'flatRent', 'officeRent', 'houseRent', 'officeSale', 'houseSale'
        ],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'ACTIVE_LK_HOMEOWNER_PRIORITY': 5,
        'WAITING_PRIORITY': 3,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': [{
                'id': 12835367,
                'cianUserId': 12835367,
                'mainAnnouncementsRegionId': 2,
                'email': 'forias@yandex.ru',
                'state': 'active',
                'stateChangeReason': None,
                'secretCode': '8321',
                'birthday': '0001-01-01T00:00:00+02:31',
                'firstName': 'Александровна',
                'lastName': 'Ирина',
                'city': None,
                'userName': None,
                'creationDate': '2017-01-20T22:22:58.913',
                'ip': 167772335,
                'externalUserSourceType': None,
                'isAgent': False
            }]}
        ),
    )
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        response=MockResponse(
             body={'items': []}
        )
    )
    await announcements_mock.add_stub(
        method='GET',
        path='/v2/get-user-active-announcements-count/',
        response=MockResponse(
            body={
                'count': 1
            }
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    client1 = await pg.fetchrow("""SELECT * FROM clients WHERE client_id = '1'""")
    client2 = await pg.fetchrow("""SELECT * FROM clients WHERE client_id = '2'""")
    client3 = await pg.fetchrow("""SELECT * FROM clients WHERE client_id = '3'""")
    client4 = await pg.fetchrow("""SELECT * FROM clients WHERE client_id = '4'""")

    offer1 = await pg.fetchrow("""SELECT * FROM offers_for_call WHERE id = '1'""")
    offer2 = await pg.fetchrow("""SELECT * FROM offers_for_call WHERE id = '2'""")
    offer3 = await pg.fetchrow("""SELECT * FROM offers_for_call WHERE id = '3'""")
    offer4 = await pg.fetchrow("""SELECT * FROM offers_for_call WHERE id = '4'""")
    offer5 = await pg.fetchrow("""SELECT * FROM offers_for_call WHERE id = '5'""")
    offer6 = await pg.fetchrow("""SELECT * FROM offers_for_call WHERE id = '6'""")

    # Добивочный клиент не удален, при том что у него пустой сегмент
    assert client1 is not None
    assert client2 is not None
    assert client3 is not None
    # Добивочный клиент не удален, при том что у него пустой региона
    assert client4 is not None

    # задание добивочного клиента не удалено даже при том что у него пустой сегмент
    # изменилась только первая и посление 2 цифры приоритета
    assert offer1['priority'] == 123456721
    assert offer2['priority'] == 131136121
    assert offer3['priority'] == 131136121
    assert offer4['priority'] == 132129521
    assert offer5['priority'] == 132129521
    # задание добивочного клиента не удалено даже при том что у него пустой регион
    # изменилась только первая и посление 2 цифры приоритета
    assert offer6['priority'] == 187654321
