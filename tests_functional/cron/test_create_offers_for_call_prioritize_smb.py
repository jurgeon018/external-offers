import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse


_CLEAR_PRIORITY = 999999999999999999


async def test_create_offers__exist_suitable_parsed_offer_and_client_agent_blocked__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    monolith_cian_profileapi_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
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
                'externalUserSourceType': 'subAgents',
                'isAgent': True
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
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is not None
    assert row['priority'] == _CLEAR_PRIORITY


async def test_create_offers__exist_suitable_parsed_offer_and_client_active_not_agent__prioritize_as_no_lk(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    monolith_cian_profileapi_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({

        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'NO_LK_SMB_PRIORITY': 1,
        'SMB_PRIORITY':  1,
        'WAITING_PRIORITY': 3,
        'MAIN_REGIONS_PRIORITY': {
            '4580': 1
        }
    })
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        response=MockResponse(
             body={'items': []}
        )
    )
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

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 231101111
    assert client_row['cian_user_id'] is None


async def test_create_offers__exist_suitable_parsed_offer_and_client_active_sub_agent__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    monolith_cian_profileapi_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
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
                'externalUserSourceType': 'subAgents',
                'isAgent': True
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
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is not None
    assert row['priority'] == _CLEAR_PRIORITY


async def test_create_offers__exist_suitable_parsed_offer_and_client_active_emls__creates_offer_with_clear_priority(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    monolith_cian_profileapi_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
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
                'isAgent': True
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
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is not None
    assert row['priority'] == _CLEAR_PRIORITY


async def test_create_offers__exist_suitable_parsed_offer_and_client_active_agent_with_0_active__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'NO_ACTIVE_SMB_PRIORITY': 2,
        'SMB_PRIORITY': 1,
        'WAITING_PRIORITY': 3
    })
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        response=MockResponse(
             body={'items': []}
        )
    )
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={
                'users': [{
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
                }]
            }
        ),
    )

    await announcements_mock.add_stub(
        method='GET',
        path='/v2/get-user-active-announcements-count/',
        response=MockResponse(
            body={
                'count': 0
            }
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 231120211
    assert client_row['cian_user_id'] == 12835367


async def test_create_offers__exist_suitable_parsed_offer_and_client_smb_without_lk__creates_waiting_offer(
    pg,
    runtime_settings,

    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'NO_LK_SMB_PRIORITY': 1,
        'WAITING_PRIORITY': 3,
        'SMB_PRIORITY': 1
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
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 231120111
    assert client_row['cian_user_id'] is None


async def test_create_offers__exist_suitable_parsed_offer_and_client_with_many_active__creates_clear_priority_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1
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
                'count': 10
            }
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
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row is not None
    assert offer_row['priority'] == _CLEAR_PRIORITY


async def test_create_offers__exist_suitable_parsed_offer_and_client_with_not_many_active__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'KEEP_PROPORTION_SMB_PRIORITY': 3,
        'WAITING_PRIORITY': 3,
        'SMB_PRIORITY': 1,
    })
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        response=MockResponse(
             body={'items': []}
        )
    )
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
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 231120311
    assert client_row['cian_user_id'] == 12835367


async def test_create_offers__exist_suitable_parsed_offer_and_client_failed_to_get_users__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
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
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row is not None
    assert offer_row['priority'] == _CLEAR_PRIORITY


async def test_create_offers__exist_suitable_parsed_offer_and_client_with_multiple_accounts__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 2,
        'KEEP_PROPORTION_SMB_PRIORITY': 3,
        'SMB_PRIORITY': 1,
        'WAITING_PRIORITY': 3
    })
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        response=MockResponse(
             body={'items': []}
        )
    )
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': [{
                'id': 12835368,
                'cianUserId': 12835368,
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
            }, {
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
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 231120311
    assert client_row['cian_user_id'] == 12835367



async def test_create_offers__exist_suitable_parsed_offer_and_client_failed_to_get_active__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'KEEP_PROPORTION_SMB_PRIORITY': 3,
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
            status=400
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
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row is not None
    assert offer_row['priority'] == _CLEAR_PRIORITY


async def test_create_offers__exist_suitable_parsed_offer_and_client_with_active_homeowner__prioritize_as_no_lk(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        'NO_LK_SMB_PRIORITY': 4,
        'SMB_PRIORITY': 1,
        'WAITING_PRIORITY': 3
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
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )

    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 231120411
    assert client_row['cian_user_id'] is None


async def test_create_offers__exist_suitable_parsed_offer_and_client_with_sanctions__doesnt_clear_client(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    monolith_cian_profileapi_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1
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
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row is not None
    assert offer_row['priority'] == _CLEAR_PRIORITY


async def test_create_offers__profile_is_blocked___offers_with_cleared_priority_created(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock
):
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 2,
    })
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        response=MockResponse(
             body={'items': []}
        )
    )
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': [{
                'id': 12835368,
                'cianUserId': 12835368,
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
            }, {
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

    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row is not None
    assert offer_row['priority'] == _CLEAR_PRIORITY


@pytest.mark.parametrize('source_type', [
    'subAgents',
    'emls',
    'n1',
    'mlsn',
])
async def test_create_offers__client_has_wrong_source_type___offers_with_cleared_priority_created(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock,
    source_type,
):
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 2,
    })
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        response=MockResponse(
             body={'items': []}
        )
    )
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': [{
                'id': 12835368,
                'cianUserId': 12835368,
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
                'externalUserSourceType': source_type,
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

    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row is not None
    assert offer_row['priority'] == _CLEAR_PRIORITY


async def test_create_offers__client_exceeds_maximum_active_offers_proportion___offers_has_clear_priority(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock,
    announcements_mock,
    monolith_cian_profileapi_mock,
):
    active_announcement_count = 10
    MAXIMUM_ACTIVE_OFFERS_PROPORTION = 1
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'MAXIMUM_ACTIVE_OFFERS_PROPORTION': MAXIMUM_ACTIVE_OFFERS_PROPORTION,
    })
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        response=MockResponse(
             body={'items': []}
        )
    )
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': [{
                'id': 12835368,
                'cianUserId': 12835368,
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
                'count': active_announcement_count
            }
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    assert offer_row is not None
    assert offer_row['priority'] == _CLEAR_PRIORITY
