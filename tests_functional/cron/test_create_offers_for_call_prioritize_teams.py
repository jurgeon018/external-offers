from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


async def test_create_offers(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    parsed_offers_for_teams,
    teams_fixture,
    monolith_cian_profileapi_mock,
    users_mock,
    announcements_mock
):
    # arrange
    # await pg.execute_scripts(parsed_offers_for_teams)
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await pg.execute_scripts(teams_fixture)
    
    await runtime_settings.set({
        # 'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        # 'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        # 'ACTIVE_LK_HOMEOWNER_PRIORITY': 5,
        # 'WAITING_PRIORITY': 3,
        # 'OFFER_TASK_CREATION_SEGMENTS': ['d'],
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
                'isAgent': False,
                # 'isAgent': True
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
    offers_for_call = await pg.fetch('''select priority, team_priorities from offers_for_call''')
    clients = await pg.fetch('''select * from clients''')
    offers_for_call = await pg.fetch('''select * from offers_for_call''')
    assert json.loads(offers_for_call[0]['team_priorities']) == {"1": -1, "2": -1, "3": -1, "4": -1, "5": -1}
    assert json.loads(offers_for_call[1]['team_priorities']) == {"1": -1, "2": -1, "3": -1, "4": -1, "5": -1}
    assert json.loads(offers_for_call[2]['team_priorities']) == {"1": -1, "2": -1, "3": -1, "4": -1, "5": -1}
    assert json.loads(offers_for_call[3]['team_priorities']) == {"1": -1, "2": -1, "3": -1, "4": -1, "5": -1}
