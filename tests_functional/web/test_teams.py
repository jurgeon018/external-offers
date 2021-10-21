import json

from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_teams(pg, http, runtime_settings):
    # arrange
    DEFAULT_MAIN_REGIONS_PRIORITY = {}
    await runtime_settings.set({
        'MAIN_REGIONS_PRIORITY': DEFAULT_MAIN_REGIONS_PRIORITY,
    })
    name = 'Команда1'
    lead_id = '1'
    new_lead_id = '2'
    new_name = 'Команда2'
    default_valid_days_after_call = None
    default_calltracking = True
    default_activation_status_position = 1
    default_promocode_price = 0
    default_categories = []
    default_regions = []
    default_segments = []
    default_subsegments = []
    default_promocode_regions = []
    default_filling = []
    default_main_regions_priority = DEFAULT_MAIN_REGIONS_PRIORITY
    new_valid_days_after_call = None
    new_calltracking = True
    new_activation_status_position = 1
    new_promocode_price = 0
    new_categories = ['1', '2', '3']
    new_regions = ['reg1', 'reg2']
    new_segments = ['c', 'b']
    new_subsegments = ['c']
    new_promocode_regions = ['region1', 'region2']
    new_filling = ['1', '2']
    new_main_regions_priority = {
        'reg1': '1',
        'reg2': '2'
    }
    # act
    # create
    create_response = await http.request(
        'POST',
        '/api/admin/v1/create-team-public/',
        json={
            'teamName': name,
            'leadId': lead_id,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    create_response = json.loads(create_response.body.decode('utf-8'))
    teams_after_creation = await pg.fetch('SELECT * FROM teams')
    after_creation_settings = json.loads(teams_after_creation[0]['settings'])
    team_id = teams_after_creation[0]['team_id']
    # read
    read_response = await http.request(
        'GET',
        f'/admin/team-card/{team_id}/',
        headers={
            'X-Real-UserId': 1,
        },
        expected_status=200
    )
    html = read_response.body.decode('utf-8')
    # update
    update_response = await http.request(
        'POST',
        '/api/admin/v1/update-team-public/',
        json={
            'teamId': team_id,
            'teamName': new_name,
            'leadId': new_lead_id,
            'validDaysAfterCall': new_valid_days_after_call,
            'calltracking': new_calltracking,
            'activationStatusPosition': new_activation_status_position,
            'promocodePrice': new_promocode_price,
            'categories': json.dumps(new_categories),
            'regions': json.dumps(new_regions),
            'segments': json.dumps(new_segments),
            'subsegments': json.dumps(new_subsegments),
            'promocodeRegions': json.dumps(new_promocode_regions),
            'filling': json.dumps(new_filling),
            'mainRegionsPriority': json.dumps(new_main_regions_priority),
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    update_response = json.loads(update_response.body.decode('utf-8'))
    teams_after_update = await pg.fetch('SELECT * FROM teams')
    after_update_settings = json.loads(teams_after_update[0]['settings'])
    # delete
    delete_response = await http.request(
        'POST',
        '/api/admin/v1/delete-team-public/',
        json={
            'teamId': team_id,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    delete_response = json.loads(delete_response.body.decode('utf-8'))
    teams_after_deletion = await pg.fetch('SELECT * FROM teams')
    # assert
    # create
    assert create_response['message'] == 'Команда была успешно создана.'
    assert create_response['success'] is True
    assert len(teams_after_creation) == 1
    assert teams_after_creation[0]['team_id'] == team_id
    assert teams_after_creation[0]['lead_id'] == lead_id
    assert teams_after_creation[0]['team_name'] == name
    assert after_creation_settings['valid_days_after_call'] == default_valid_days_after_call
    assert after_creation_settings['calltracking'] == default_calltracking
    assert after_creation_settings['activation_status_position'] == default_activation_status_position
    assert after_creation_settings['promocode_price'] == default_promocode_price
    assert after_creation_settings['categories'] == default_categories
    assert after_creation_settings['regions'] == default_regions
    assert after_creation_settings['segments'] == default_segments
    assert after_creation_settings['subsegments'] == default_subsegments
    assert after_creation_settings['promocode_regions'] == default_promocode_regions
    assert after_creation_settings['filling'] == default_filling
    assert after_creation_settings['main_regions_priority'] == default_main_regions_priority
    # read
    assert html is not None
    # update
    assert update_response['success'] is True
    assert update_response['message'] == 'Информация про команду была успешно обновлена.'
    assert len(teams_after_update) == 1
    assert teams_after_update[0]['team_id'] == team_id
    assert teams_after_update[0]['lead_id'] == new_lead_id
    assert teams_after_update[0]['team_name'] == new_name
    assert after_update_settings['valid_days_after_call'] == new_valid_days_after_call
    assert after_update_settings['calltracking'] == new_calltracking
    assert after_update_settings['activation_status_position'] == new_activation_status_position
    assert after_update_settings['promocode_price'] == new_promocode_price
    assert after_update_settings['categories'] == new_categories
    assert after_update_settings['regions'] == new_regions
    assert after_update_settings['segments'] == new_segments
    assert after_update_settings['subsegments'] == new_subsegments
    assert after_update_settings['promocode_regions'] == new_promocode_regions
    assert after_update_settings['filling'] == new_filling
    assert after_update_settings['main_regions_priority'] == new_main_regions_priority
    # delete
    assert delete_response['success'] is True
    assert delete_response['message'] == 'Команда была успешно удалена.'
    assert len(teams_after_deletion) == 0


async def test_render_teams(
    http, users_mock,
):
    # arrange
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-userids-by-rolename/',
        response=MockResponse(
            body={'userIds': []}
        ),
    )
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-users/',
        response=MockResponse(
            body={'users': []}
        ),
    )
    await users_mock.add_stub(
        method='GET',
        path='/v1/user-has-role/',
        response=MockResponse(
            body=True
        ),
    )
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-userids-by-rolename/',
        response=MockResponse(
            body={
                'roleName': []
            }
        )
    )
    await users_mock.add_stub(
        method='POST',
        path='/v1/get-users/',
        response=MockResponse(
            body={
                'users': []
            }
        )
    )

    # act
    resp = await http.request(
        'GET',
        '/admin/teams/',
        headers={
            'X-Real-UserId': 100,
        },
        expected_status=200
    )
    html = resp.body.decode('utf-8')
    # assert
    assert html is not None
