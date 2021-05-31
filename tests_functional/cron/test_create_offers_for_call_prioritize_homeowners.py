from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_create_offers__exist_suitable_parsed_offer_and_client_with_active_lk__creates_waiting_offer2(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
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
                'externalUserSourceType': 'emls',
                'isAgent': False
            }]}
        ),
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
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 322005
    assert client_row['cian_user_id'] == 12835367


async def test_create_offers__exist_suitable_parsed_offer_and_client_with_active_lk__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
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
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 322005
    assert client_row['cian_user_id'] == 12835367


async def test_create_offers__exist_suitable_parsed_offer_and_client_with_blocked_lk__clears_client(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'ACTIVE_LK_HOMEOWNER_PRIORITY': 5
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
                'state': 'blocked',
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
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row is None


async def test_create_offers__exist_suitable_parsed_offer_and_client_with_active_agent__prioritize_as_no_lk(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'NO_LK_HOMEOWNER_PRIORITY': 4,
        'WAITING_PRIORITY': 3,
        'HOMEOWNER_PRIORITY': 2

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
                'isAgent': True
            }]}
        ),
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
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 322004
    assert client_row['cian_user_id'] is None


async def test_create_offers__exist_suitable_parsed_offer_and_client_failed_to_get_users__cleares_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            status=400
        )
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row is None


async def test_create_offers__exist_suitable_parsed_offer_and_client_homeowner_without_lk__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'NO_LK_HOMEOWNER_PRIORITY': 4,
        'WAITING_PRIORITY': 3,
        'HOMEOWNER_PRIORITY': 2
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 322004
    assert client_row['cian_user_id'] is None
