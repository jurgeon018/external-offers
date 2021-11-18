from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


_CLEAR_PRIORITY = -1


async def test_team_priorities(
    pg,
    http,
    runtime_settings,
    runner,
    parsed_offers_for_teams,
    monolith_cian_profileapi_mock,
    users_mock,
    announcements_mock,
):
    # arrange
    OFFER_TASK_CREATION_SEGMENTS = ['c']
    OFFER_TASK_CREATION_CATEGORIES = ['flatSale', 'officeSale', 'houseSale', 'officeRent']
    OFFER_TASK_CREATION_REGIONS = [4580, 184723]
    NO_ACTIVE_SMB_PRIORITY = 2
    SMB_PRIORITY = 1
    WAITING_PRIORITY = 3
    cian_user_id = 12835367
    operator_id = 1
    await runtime_settings.set({
        'ENABLE_TEAM_PRIORITIES': True,
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'OFFER_TASK_CREATION_SEGMENTS': OFFER_TASK_CREATION_SEGMENTS,
        'OFFER_TASK_CREATION_CATEGORIES': OFFER_TASK_CREATION_CATEGORIES,
        'OFFER_TASK_CREATION_REGIONS': OFFER_TASK_CREATION_REGIONS,
        'NO_ACTIVE_SMB_PRIORITY': NO_ACTIVE_SMB_PRIORITY,
        'SMB_PRIORITY': SMB_PRIORITY,
        'WAITING_PRIORITY': WAITING_PRIORITY,
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

    # создать спаршеные обьявления
    await pg.execute_scripts(parsed_offers_for_teams)

    # создать команды, операторов и настройки
    await prepare_teams(http=http, pg=pg, operator_id=operator_id)

    # создать задания для прозвона
    await assert_offers_creation(runner=runner, pg=pg, cian_user_id=cian_user_id)

    # взять задания в работу
    # await assert_offers_updating(pg=pg, http=http, operator_id=operator_id)

    # протестить весь флоу админки:
    #   - TODO: отправить в перезвон
    #   - TODO: взять в работу
    #   - TODO: сохранить обьявление
    #   - TODO: проверить добивочность


async def prepare_teams(*, http, pg, operator_id):
    # создать несколько операторов(по 1 оператору на каждую команду)
    teams_amount = 5
    for i in range(teams_amount):
        await http.request(
            'POST',
            '/api/admin/v1/create-operator-public/',
            json={
                'operatorId': str(i),
                'fullName': f'Оператор №{i+1}',
                'teamId': str(i),
            },
            headers={
                'X-Real-UserId': operator_id
            },
            expected_status=200
        )

    # создать несколько команд через ручку
    # (если делать через pg.execute то придется руками прописывать большое количество дефолтных параметров)
    for i in range(teams_amount):
        await http.request(
            'POST',
            '/api/admin/v1/create-team-public/',
            json={
                'teamName': f'Команда №{i+1}',
                'leadId': str(i),
            },
            headers={
                'X-Real-UserId': operator_id
            },
            expected_status=200
        )

    # проставить разные настройки разным командам
    # TODO: прописать валидные значения категорий
    # TODO: прописать валидные значения регионов
    await update_team_settings(team_id=1, key='regions', value='[4580]', pg=pg)
    await update_team_settings(team_id=2, key='segments', value='["d"]', pg=pg)
    await update_team_settings(team_id=3, key='categories', value='["officeRent"]', pg=pg)
    await update_team_settings(team_id=4, key='flat_priority', value='3', pg=pg)
    await update_team_settings(team_id=4, key='suburban_priority', value='2', pg=pg)
    await update_team_settings(team_id=4, key='commercial_priority', value='1', pg=pg)
    await update_team_settings(team_id=5, key='sale_priority', value='2', pg=pg)
    await update_team_settings(team_id=5, key='rent_priority', value='1', pg=pg)
    # for x in await pg.fetch("""
    #     select
    #         team_id,
    #         settings->'regions' as regions,
    #         settings->'segments' as segments,
    #         settings->'categories' as categories,
    #         settings->'flat_priority' as flat_priority,
    #         settings->'suburban_priority' as suburban_priority,
    #         settings->'commercial_priority' as commercial_priority,
    #         settings->'sale_priority' as sale_priority,
    #         settings->'rent_priority' as rent_priority
    #     from teams
    # """):
    #     print('\n teams: \n', x)


async def assert_offers_creation(*, runner, pg, cian_user_id):
    # создать задания из спаршеных обьявлений(через крон)
    await runner.run_python_command('create-offers-for-call')

    # проверить что задания создаются
    ofc = await pg.fetch("""select * from offers_for_call""")
    assert len(ofc) == 8

    # проверить что клиенты создаются
    clients = await pg.fetch("""select * from clients""")
    assert len(clients) == 4

    assert clients[0]['status'] == 'waiting'
    assert clients[1]['status'] == 'waiting'
    assert clients[2]['status'] == 'waiting'
    assert clients[3]['status'] == 'waiting'
    rows = await pg.fetch('select status from offers_for_call')
    statuses = [row['status'] for row in rows]
    assert len(set(statuses)) == 1
    assert statuses[0] == 'waiting'

    ofc1 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'894ff03a-573c-4bac-8599-28f17e68a0d8\''
    )
    ofc2 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'1d6c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc3 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'2d6c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc4 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'3d6c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc5 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'996c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc6 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'7b6c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc7 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'126c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc8 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'2e6c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc9 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'3e6c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc10 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'4e6c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc11 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'575ff03a-573c-4bac-8599-28f17e68a0d8\''
    )
    ofc12 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'9d6c73b8-3057-47cc-b50a-419052da619f\''
    )
    ofc13 = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE parsed_id = \'821ff03a-573c-4bac-8599-28f17e68a0d8\''
    )

    # задание не создалось изза is_calltracking==True
    assert ofc6 is None
    # задание не создалось изза synced==True
    assert ofc7 is None
    # задание не создалось изза "phones": null
    assert ofc8 is None
    # задание не создалось изза "phones": [""]
    assert ofc9 is None
    # задание не создалось изза "phones": []
    assert ofc10 is None

    # TODO: мануально проверить что проставился правильный приоритет
    assert ofc1['priority'] == 231115211
    assert ofc2['priority'] == 231120211
    assert ofc3['priority'] == 231120211
    assert ofc4['priority'] == 231120211
    assert ofc5['priority'] == 231120211
    assert ofc11['priority'] == _CLEAR_PRIORITY
    assert ofc12['priority'] == 231120212
    assert ofc13['priority'] == 231115223
    assert json.loads(ofc1['team_priorities']) == {
        '1': -1, '2': 231115211, '3': 231115211, '4': 231115211, '5': 231115211
    }
    assert json.loads(ofc2['team_priorities']) == {
        '1': 231120211, '2': 231120211, '3': -1, '4': 231120211, '5': 231120211
    }
    assert json.loads(ofc3['team_priorities']) == {
        '1': 231120211, '2': 231120211, '3': -1, '4': 231120211, '5': 231120211
    }
    assert json.loads(ofc4['team_priorities']) == {
        '1': 231120211, '2': 231120211, '3': -1, '4': 231120211, '5': 231120211
    }
    assert json.loads(ofc5['team_priorities']) == {
        '1': 231120211, '2': 231120211, '3': -1, '4': 231120211, '5': 231120211
    }
    assert json.loads(ofc11['team_priorities']) == {
        '1': -1, '2': -1, '3': -1, '4': -1, '5': -1
    }
    assert json.loads(ofc12['team_priorities']) == {
        '1': 231120212, '2': 231120212, '3': -1, '4': 231120212, '5': 231120212
    }
    assert json.loads(ofc13['team_priorities']) == {
        '1': -1, '2': 231115223, '3': 231115223, '4': 231115223, '5': 231115223
    }


async def assert_offers_updating(*, pg, http, operator_id):
    # взять клиента и задания в работу
    # TODO: проверить выдачу в работу
    # TODO: проверить выдачу комерческих обьявлений
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
    clients = await pg.fetch("""select * from clients""")
    ofc = await pg.fetch("""select * from offers_for_call""")
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


async def update_team_settings(*, key, value, team_id, pg):
    await pg.execute(f"""
    UPDATE teams SET settings = jsonb_set(
        coalesce(settings, '{{}}'),
        '{{{key}}}',
        '{value}'
    )
    WHERE team_id = {team_id};
    """)
