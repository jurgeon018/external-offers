import pytest
from cian_functional_test_utils.helpers import ANY
from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


_CLEAR_PRIORITY = 99999999999999999999


@pytest.mark.parametrize('use_gather_for_priority_clients', [True, False])
async def test_create_offers__exist_suitable_parsed_offer_and_client_with_emls__clears_client(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    use_gather_for_priority_clients,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'ACTIVE_LK_HOMEOWNER_PRIORITY': 5,
        'WAITING_PRIORITY': 3,
        'USE_GATHER_FOR_PRIORITY_CLIENTS': use_gather_for_priority_clients,
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
    assert offer_row['priority'] == _CLEAR_PRIORITY


@pytest.mark.parametrize('use_cached_clients_priority, use_gather_for_priority_clients', [
    (True, True),
    (False, True),
    (True, False),
    (False, False),
])
async def test_create_offers__exist_suitable_parsed_offer_and_client_with_active_lk__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock,
    use_cached_clients_priority,
    use_gather_for_priority_clients,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
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
        'USE_CACHED_CLIENTS_PRIORITY': use_cached_clients_priority,
        'USE_GATHER_FOR_PRIORITY_CLIENTS': use_gather_for_priority_clients,
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
    assert offer_row['priority'] == 232120512
    assert client_row['cian_user_id'] == 12835367


@pytest.mark.parametrize('use_gather_for_priority_clients', [True, False])
async def test_create_offers__exist_suitable_parsed_offer_and_client_with_blocked_lk__clears_client(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    use_gather_for_priority_clients,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'ACTIVE_LK_HOMEOWNER_PRIORITY': 5,
        'USE_GATHER_FOR_PRIORITY_CLIENTS': use_gather_for_priority_clients,
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

    assert offer_row['priority'] == _CLEAR_PRIORITY


@pytest.mark.parametrize('use_gather_for_priority_clients', [True, False])
async def test_create_offers__exist_suitable_parsed_offer_and_client_with_active_agent__prioritize_as_no_lk(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock,
    use_gather_for_priority_clients,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': [
            'flatSale', 'flatRent', 'officeRent', 'houseRent', 'officeSale', 'houseSale'
        ],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'NO_LK_HOMEOWNER_PRIORITY': 4,
        'WAITING_PRIORITY': 3,
        'HOMEOWNER_PRIORITY': 2,
        'USE_CACHED_CLIENTS_PRIORITY': True,
        'USE_GATHER_FOR_PRIORITY_CLIENTS': use_gather_for_priority_clients,
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

    cached_priorities_before_cron = await pg.fetch("""
        SELECT * FROM clients_priorities;
    """)
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
    offer_priority_part = '12'
    client_priority_part = '2321204'
    expected_priority = client_priority_part + offer_priority_part
    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 232120412
    assert client_row['cian_user_id'] is None

    cached_priorities = await pg.fetch("""
        SELECT * FROM clients_priorities;
    """)

    # До запуска крона в базе небыло закешированых приоритетов
    assert len(cached_priorities_before_cron) == 0
    # После запуска крона в базе закешировались приоритеты
    assert len(cached_priorities) == 1
    client_id = client_row['client_id']
    assert cached_priorities[0] == {
        'team_id': None,
        'priorities': f'{{"{client_id}": "{int(client_priority_part)}"}}',
        'created_at': ANY,
        'updated_at': ANY,
    }
    # проставляет пустой приоритет клиенту, чтобы повторно протестить приоретизацию из закешированых приоритетов
    await pg.execute("""
        UPDATE offers_for_call SET priority = null WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
    """)
    offer_priority = await pg.fetchval("""
        SELECT priority FROM offers_for_call WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
    """)
    assert offer_priority is None

    await runner.run_python_command('create-offers-for-call')
    cached_client_priority = await pg.fetchval("""
        SELECT priorities FROM clients_priorities LIMIT 1
    """)
    offer_priority = await pg.fetchval("""
        SELECT priority FROM offers_for_call WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
    """)
    assert offer_priority == int(expected_priority)
    assert int(json.loads(cached_client_priority)[client_id]) == int(str(offer_priority)[0:-2])


@pytest.mark.parametrize('use_gather_for_priority_clients', [True, False])
async def test_create_offers__exist_suitable_parsed_offer_and_client_failed_to_get_users__cleares_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    use_gather_for_priority_clients,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'USE_GATHER_FOR_PRIORITY_CLIENTS': use_gather_for_priority_clients,
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

    assert offer_row['priority'] == _CLEAR_PRIORITY


@pytest.mark.parametrize('use_gather_for_priority_clients', [True, False])
async def test_create_offers__exist_suitable_parsed_offer_and_client_homeowner_without_lk__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    use_gather_for_priority_clients,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': [
            'flatSale', 'flatRent', 'officeRent', 'houseRent', 'officeSale', 'houseSale'
        ],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'NO_LK_HOMEOWNER_PRIORITY': 4,
        'WAITING_PRIORITY': 3,
        'HOMEOWNER_PRIORITY': 2,
        'USE_CACHED_CLIENTS_PRIORITY': True,
        'USE_GATHER_FOR_PRIORITY_CLIENTS': use_gather_for_priority_clients,
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
    assert offer_row['priority'] == 232120412
    assert client_row['cian_user_id'] is None


@pytest.mark.parametrize('use_gather_for_priority_clients', [True, False])
async def test_create_offers__exist_suitable_parsed_offer_and_client_with_sanctions__clears_client(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    monolith_cian_profileapi_mock,
    use_gather_for_priority_clients,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'ACTIVE_LK_HOMEOWNER_PRIORITY': 5,
        'USE_GATHER_FOR_PRIORITY_CLIENTS': use_gather_for_priority_clients,
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
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        response=MockResponse(
            body={'items': [{
                'userId': 12835367,
                'sanctions': [
                    {
                        'sanctionId': 9072881,
                        'sanctionName': 'Запрет на публикацию объявлений',
                        'sanctionEnd': None
                    }
                ]
            }]}
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

    assert offer_row['priority'] == _CLEAR_PRIORITY


@pytest.mark.parametrize('use_gather_for_priority_clients', [True, False])
async def test_create_offers__clear_homeowners_with_existing_accounts_is_true__clients_cleared(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    use_gather_for_priority_clients,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': True,
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'ACTIVE_LK_HOMEOWNER_PRIORITY': 5,
        'USE_GATHER_FOR_PRIORITY_CLIENTS': use_gather_for_priority_clients,
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

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row['priority'] == _CLEAR_PRIORITY
