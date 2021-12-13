from datetime import datetime, timedelta

import pytz
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
        'ENABLE_TEAMS_PRIORITIZATION': True,
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
    await assert_offers_updating(pg=pg, http=http, operator_id=operator_id)


async def prepare_teams(*, http, pg, operator_id):
    # создать несколько операторов(по 1 оператору на каждую команду)
    teams_amount = 5
    for i in range(teams_amount):
        await pg.execute("""
        INSERT INTO operators (
            operator_id, full_name, team_id, is_teamlead, created_at, updated_at
        ) VALUES (
            $1, $2, $3, 't', 'now()', 'now()'
        )
        """, [str(i), f'Оператор №{i+1}', i])

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
    await update_team_settings(team_id=1, key='regions', value='[4580]', pg=pg)
    await update_team_settings(team_id=2, key='segments', value='["d"]', pg=pg)
    await update_team_settings(team_id=3, key='categories', value='["officeRent"]', pg=pg)
    await update_team_settings(team_id=4, key='flat_priority', value='3', pg=pg)
    await update_team_settings(team_id=4, key='suburban_priority', value='2', pg=pg)
    await update_team_settings(team_id=4, key='commercial_priority', value='1', pg=pg)
    await update_team_settings(team_id=5, key='sale_priority', value='2', pg=pg)
    await update_team_settings(team_id=5, key='rent_priority', value='1', pg=pg)


async def prepare_unactivated_clients(*, runner, pg):
    await pg.execute("""
    INSERT INTO public.clients (
        client_id,
        avito_user_id,
        client_name,
        client_phones,
        client_email,
        operator_user_id,
        status,
        calls_count,
        last_call_id,
        unactivated
    ) VALUES(
        'unactivated_client_id_1',
        '92131321',
        'АлександрАлександров',
        '{+79812333237}',
        'testemail@gmail.com',
        60024636,
        'waiting',
        1,
        NULL,
        TRUE
    );
    """)
    await pg.execute("""
    INSERT INTO public.offers_for_call (
        id,
        parsed_id,
        client_id,
        status,
        created_at,
        started_at,
        synced_at,
        priority,
        last_call_id,
        synced_with_kafka,
        category,
        publication_status
    ) VALUES(
        545222,
        'xdd86dec-20f5-4a70-bb3a-077b2754dfe6',
        'unactivated_client_id_1',
        'waiting',
        '2020-10-11 04:05:06',
        '2020-10-11 04:05:06',
        '2020-10-11 04:05:06',
        1,
        NULL,
        false,
        NULL,
        'Draft'
    );
    """)
    team_id = '1'
    priority = '1234'
    offer_id = 545222
    query = """
    UPDATE offers_for_call
    SET team_priorities = jsonb_set(
        coalesce(team_priorities, '{}'),
        '{%s}',
        '%s'
    )
    WHERE id = '%s';
    """ % (
        team_id,
        priority,
        offer_id,
    )
    await pg.execute(query)


async def assert_offers_creation(*, runner, pg, cian_user_id):
    # создать добивочные задания
    await prepare_unactivated_clients(runner=runner, pg=pg)

    # создать задания из спаршеных обьявлений(через крон)
    await runner.run_python_command('create-offers-for-call')

    # проверить что клиенты создаются
    clients = await pg.fetch("""
        SELECT status FROM clients WHERE avito_user_id IN (
            'c42bb598767308327e1dffbe7241486c',
            '555bb598767308327e1dffbe7241486c',
            '29f05f430722c915c498113b16ba0e78',
            '25f05f430722c915c498113b16ba0e78'
        )
    """)
    assert [client['status'] for client in clients][0] == 'waiting'
    assert len({client['status'] for client in clients}) == 1
    offer_statuses = await pg.fetch('select status from offers_for_call')
    offer_statuses = [row['status'] for row in offer_statuses]
    assert len(set(offer_statuses)) == 1
    assert offer_statuses[0] == 'waiting'
    assert await pg.fetchval("""select count(*) from clients""") == 5

    # проверить что задания создаются
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

    assert ofc1['priority'] == 231115211
    assert ofc2['priority'] == 231120211
    assert ofc3['priority'] == 231120211
    assert ofc4['priority'] == 231120211
    assert ofc5['priority'] == 231120211
    assert ofc11['priority'] == _CLEAR_PRIORITY
    assert ofc12['priority'] == 231120212
    assert ofc13['priority'] == 231115223
    assert await pg.fetchval('select count(*) from offers_for_call') == 9
    assert json.loads(ofc1['team_priorities']) == {
        '1': -1, '2': -1, '3': 231115211, '4': 231115213, '5': 231115221
    }
    assert json.loads(ofc2['team_priorities']) == {
        '1': 231120211, '2': 231120211, '3': -1, '4': 231120213, '5': 231120221
    }
    assert json.loads(ofc3['team_priorities']) == {
        '1': 231120211, '2': 231120211, '3': -1, '4': 231120213, '5': 231120221
    }
    assert json.loads(ofc4['team_priorities']) == {
        '1': 231120211, '2': 231120211, '3': -1, '4': 231120213, '5': 231120221
    }
    assert json.loads(ofc5['team_priorities']) == {
        '1': 231120211, '2': -1, '3': -1, '4': 231120213, '5': 231120221
    }
    assert json.loads(ofc11['team_priorities']) == {
        '1': -1, '2': -1, '3': -1, '4': -1, '5': -1
    }
    assert json.loads(ofc12['team_priorities']) == {
        '1': 231120212, '2': 231120212, '3': -1, '4': 231120212, '5': 231120222
    }
    assert json.loads(ofc13['team_priorities']) == {
        '1': -1, '2': -1, '3': 231115223, '4': 231115221, '5': 231115213
    }


async def assert_offers_updating(*, pg, http, operator_id):
    # взять клиента и задания в работу
    team_id = 1
    operator_team_id = await pg.fetchval("""
        SELECT team_id FROM operators WHERE operator_id=$1;
    """, [str(operator_id)])
    assert operator_team_id == team_id
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_id
        },
        json={},
        expected_status=200
    )
    clients = await pg.fetch("""
        select status, team_id from clients where avito_user_id in (
            'c42bb598767308327e1dffbe7241486c',
            '555bb598767308327e1dffbe7241486c',
            '25f05f430722c915c498113b16ba0e78'
        )
    """)
    ofc = await pg.fetchrow("""
        select * from offers_for_call where parsed_id='996c73b8-3057-47cc-b50a-419052da619f'
    """)
    client = await pg.fetchrow("""select * from clients where avito_user_id = '29f05f430722c915c498113b16ba0e78'""")
    assert resp.data['errors'] == []
    assert resp.data['success']
    statuses = [client['status'] for client in clients]
    team_ids = [client['team_id'] for client in clients]
    assert len(set(statuses)) == 1
    assert statuses[0] == 'waiting'
    assert len(set(team_ids)) == 1
    assert team_ids[0] is None
    assert client['status'] == 'inProgress'
    assert client['team_id'] == team_id
    assert ofc['status'] == 'inProgress'
    ofc = await pg.fetchrow("""
        select * from offers_for_call where parsed_id='996c73b8-3057-47cc-b50a-419052da619f'
    """)
    # отправить в перезвон
    dt = datetime.now(pytz.utc) - timedelta(days=4)
    call_later_datetime = dt.isoformat()

    _call_later_status_response = await _set_call_later_status_for_client(
        http=http,
        operator_id=operator_id,
        client_id=client['client_id'],
        call_later_datetime=call_later_datetime,
    )
    assert _call_later_status_response['success'] is True
    assert _call_later_status_response['errors'] == []
    ofc = await pg.fetchrow("""
        select * from offers_for_call where parsed_id='996c73b8-3057-47cc-b50a-419052da619f'
    """)
    client = await pg.fetchrow("""
        select * from clients where client_id=$1
    """, [client['client_id']])
    assert client['operator_user_id'] == operator_id
    assert client['status'] == 'callLater'
    assert client['next_call'].date() == dt.date()
    assert ofc['status'] == 'callLater'
    # взять в работу
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_id
        },
        json={},
        expected_status=200
    )
    resp = json.loads(resp.body.decode('utf-8'))
    assert resp['success'] is True
    assert resp['errors'] == []
    ofc = await pg.fetchrow("""
        select * from offers_for_call where parsed_id='996c73b8-3057-47cc-b50a-419052da619f'
    """)
    client = await pg.fetchrow("""
        select * from clients where client_id=$1
    """, [client['client_id']])
    assert client['status'] == 'inProgress'
    assert client['team_id'] == team_id
    assert ofc['status'] == 'inProgress'
    assert ofc['priority'] == 231120211
    new_priority = 100000
    assert json.loads(ofc['team_priorities']) == {
        '1': new_priority, '2': -1, '3': -1, '4': 231120213, '5': 231120221
    }


async def update_team_settings(*, key, value, team_id, pg):
    await pg.execute(f"""
    UPDATE teams SET settings = jsonb_set(
        coalesce(settings, '{{}}'),
        '{{{key}}}',
        '{value}'
    )
    WHERE team_id = {team_id};
    """)


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
