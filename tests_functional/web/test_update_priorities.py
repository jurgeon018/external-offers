import asyncio

import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


@pytest.mark.parametrize('is_test_request, is_test_value', [
    (None, 'f'),
    (True, 't'),
])
async def test_update_team_priorities(
    http,
    pg,
    runner,
    parsed_offers_for_teams,
    users_mock,
    monolith_cian_profileapi_mock,
    announcements_mock,
    is_test_request,
    is_test_value,
):
    cian_user_id = 12345
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )
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
                    'id': cian_user_id,
                    'cianUserId': cian_user_id,
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

    await pg.execute_scripts(parsed_offers_for_teams)

    await runner.run_python_command('create-offers-for-call')

    await pg.execute(f"""
    UPDATE offers_for_call SET is_test='{is_test_value}';
    UPDATE clients SET is_test='{is_test_value}';
    UPDATE parsed_offers SET is_test='{is_test_value}';
    """)
    await http.request(
        'POST',
        '/api/admin/v1/create-team-public/',
        json={
            'teamName': 'team 1',
            'leadId': '1',
        },
        headers={
            'X-Real-UserId': 1
        },
    )
    team_id = await pg.fetchval('select team_id from teams limit 1')

    await update_team_settings(team_id=team_id, key='regions', value='[4580]', pg=pg)
    await update_team_settings(team_id=team_id, key='segments', value='["c"]', pg=pg)
    await update_team_settings(team_id=team_id, key='categories', value='["flatSale"]', pg=pg)
    ofc = await pg.fetchrow("""
    select * from offers_for_call
    where parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
    """)
    assert ofc['team_priorities'] is None

    resp = await http.request(
        'POST',
        '/api/admin/v1/prioritize-waiting-offers-public/',
        json={
            'teamId': str(team_id),
            'isTest': is_test_request,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    response = json.loads(resp.body.decode('utf-8'))

    assert response['success'] is True
    assert response['message'] == f'Проставление приоритетов для команды {team_id} было запущено'

    await asyncio.sleep(1)
    ofc = await pg.fetchrow("""
    select * from offers_for_call
    where parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
    """)
    assert json.loads(ofc['team_priorities'])[str(team_id)] == 231120212



@pytest.mark.parametrize('is_test_request, is_test_value', [
    (None, 'f'),
    (True, 't'),
])
async def test_update_priorities(
    http,
    pg,
    runner,
    parsed_offers_for_teams,
    users_mock,
    monolith_cian_profileapi_mock,
    announcements_mock,
    is_test_request,
    is_test_value,
    runtime_settings,
):
    cian_user_id = 12345
    await runtime_settings.set({
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale'],
    })
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )
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
                    'id': cian_user_id,
                    'cianUserId': cian_user_id,
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

    await pg.execute_scripts(parsed_offers_for_teams)

    await runner.run_python_command('create-offers-for-call')

    await pg.execute(f"""
    UPDATE offers_for_call SET priority=NULL;
    UPDATE offers_for_call SET is_test='{is_test_value}';
    UPDATE clients SET is_test='{is_test_value}';
    UPDATE parsed_offers SET is_test='{is_test_value}';
    """)
    await http.request(
        'POST',
        '/api/admin/v1/create-team-public/',
        json={
            'teamName': 'team 1',
            'leadId': '1',
        },
        headers={
            'X-Real-UserId': 1
        },
    )

    ofc = await pg.fetchrow("""
    select * from offers_for_call
    where parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
    """)
    assert ofc['priority'] is None

    resp = await http.request(
        'POST',
        '/api/admin/v1/prioritize-waiting-offers-public/',
        json={
            'isTest': is_test_request,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    response = json.loads(resp.body.decode('utf-8'))

    assert response['success'] is True
    assert response['message'] == f'Проставление приоритетов было запущено'

    await asyncio.sleep(1)
    ofc = await pg.fetchrow("""
    select * from offers_for_call
    where parsed_id = '9d6c73b8-3057-47cc-b50a-419052da619f'
    """)
    assert ofc['priority'] == 231120212


async def update_team_settings(*, key, value, team_id, pg):
    await pg.execute(f"""
    UPDATE teams SET settings = jsonb_set(
        coalesce(settings, '{{}}'),
        '{{{key}}}',
        '{value}'
    )
    WHERE team_id = {team_id};
    """)
