from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


def _print(objects, table=None):
    print()
    print('loop start')
    for obj in objects:
        print(f'\n{"№": <30}{objects.index(obj)+1}')
        for key, value in obj.items():
            if table == 'ofc':
                print('{table}.{key: <30}{value}'.format(table=table, key=key, value=value))
            elif table == 'clients':
                print('{table}.{key: <22}{value}'.format(table=table, key=key, value=value))
            else:
                print('{table}.{key: <30}{value}'.format(table=table, key=key, value=value))
    print('loop end')


async def test_team_priorities(
    pg,
    http,
    offers_and_clients_fixture,
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


    cian_user_id = 12835367
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        # 'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent', 'officeRent'],
        # 'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580, 184723],
        # 'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'NO_ACTIVE_SMB_PRIORITY': 2,
        'SMB_PRIORITY': 1,
        'WAITING_PRIORITY': 3,
        'ENABLE_TEAM_PRIORITIES': True,
        # 'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        # 'MAXIMUM_ACTIVE_OFFERS_PROPORTION': 1,
        # 'ACTIVE_LK_HOMEOWNER_PRIORITY': 5,
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


    # act & assert


    # создать операторов и команды(TODO переделать через ручку)
    # print('создать операторов и команды')
    await pg.execute_scripts(teams_fixture)
    # print('\n\n\n')


    # создать спаршеные обьявления(TODO переделать через консьюмер)
    # print('создать спаршеные обьявления')
    await pg.execute_scripts(parsed_offers_for_teams)
    # await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    # print('\n\n\n')


    # создать задания из спаршеных обьявлений(через крон)
    # print('создать задания из спаршеных обьявлений')
    await runner.run_python_command('create-offers-for-call')
    clients = await pg.fetch('''select * from clients''')
    ofc = await pg.fetch('''select * from offers_for_call''')
    # _print(ofc, table='ofc')
    # _print(clients, table='clients')
    # проверить что задания создаются
    assert len(ofc) == 6
    # проверить что клиенты создаются
    assert len(clients) == 3
    # проверить что проставились правильные приоритеты
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
    assert client_row['cian_user_id'] == cian_user_id
    assert clients[0]['status'] == 'waiting'
    assert clients[1]['status'] == 'waiting'
    assert clients[2]['status'] == 'waiting'
    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 231120211
    assert ofc[0]['priority'] == 231120211
    assert ofc[1]['priority'] == 231120211
    assert ofc[2]['priority'] == 231120211
    assert ofc[3]['priority'] == 231120211
    assert ofc[4]['priority'] == 231115223
    assert ofc[5]['priority'] == 231115211
    # TODO: https://jira.cian.tech/browse/CD-116915/
    # проверить разные приритеты команд
    assert json.loads(ofc[0]['team_priorities']) == {"1": 231120211, "2": 231120211, "3": 231120211, "4": 231120211, "5": 231120211}
    assert json.loads(ofc[1]['team_priorities']) == {"1": 231120211, "2": 231120211, "3": 231120211, "4": 231120211, "5": 231120211}
    assert json.loads(ofc[2]['team_priorities']) == {"1": 231120211, "2": 231120211, "3": 231120211, "4": 231120211, "5": 231120211}
    assert json.loads(ofc[3]['team_priorities']) == {"1": 231120211, "2": 231120211, "3": 231120211, "4": 231120211, "5": 231120211}
    assert json.loads(ofc[4]['team_priorities']) == {"1": 231115223, "2": 231115223, "3": 231115223, "4": 231115223, "5": 231115223}
    assert json.loads(ofc[5]['team_priorities']) == {"1": 231115211, "2": 231115211, "3": 231115211, "4": 231115211, "5": 231115211}
    # print('\n\n\n')


    # взять клиента и задания в работу
    # print('взять клиента и задания в работу')
    operator_id = 73478905
    operator_team_id = await pg.fetchval("""
        SELECT team_id FROM operators WHERE operator_id=$1;
    """, [str(operator_id)])
    assert operator_team_id
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_id
        },
        json={},
        expected_status=200
    )
    clients = await pg.fetch('''select * from clients''')
    ofc = await pg.fetch('''select * from offers_for_call''')
    # _print(ofc, table='ofc')
    # _print(clients, table='clients')
    assert resp.data['errors'] == []
    assert resp.data['success']
    assert len(ofc) == 6
    assert len(clients) == 3
    assert clients[0]['status'] == 'waiting'
    assert clients[1]['status'] == 'waiting'
    assert clients[2]['status'] == 'inProgress'
    assert clients[0]['team_id'] is None
    assert clients[1]['team_id'] is None
    assert clients[2]['team_id'] == operator_team_id
    assert ofc[0]['status'] == 'waiting'
    assert ofc[1]['status'] == 'waiting'
    assert ofc[2]['status'] == 'waiting'
    assert ofc[3]['status'] == 'waiting'
    assert ofc[4]['status'] == 'inProgress'
    assert ofc[5]['status'] == 'inProgress'
    # print('\n\n\n')

    # TODO: https://jira.cian.tech/browse/CD-116915/
    # - протестить весь флоу админки:
    #   - отправить в перезвон
    #   - взять в работу
    #   - сохранить обьявление
    #   - проверить добивочность
