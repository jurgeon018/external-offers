import json

from cian_functional_test_utils.pytest_plugin import MockResponse
import pytest


async def test_teams(pg, http):
    # arrange
    name = 'Команда1'
    lead_id = '1'
    segment = 'c'
    new_lead_id = '2'
    new_name = 'Команда2'
    new_segment = 'd'
    # act
    # create
    create_response = await http.request(
        'POST',
        '/api/admin/v1/create-team-public/',
        json={
            'teamName': name,
            'leadId': lead_id,
            'segment': segment,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    create_response = json.loads(create_response.body.decode('utf-8'))
    teams_after_creation = await pg.fetch('SELECT * FROM teams')
    team_id = teams_after_creation[0]['team_id']
    # update
    update_response = await http.request(
        'POST',
        '/api/admin/v1/update-team-public/',
        json={
            'teamId': team_id,
            'teamName': new_name,
            'leadId': new_lead_id,
            'segment': new_segment,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    update_response = json.loads(update_response.body.decode('utf-8'))
    teams_after_update = await pg.fetch('SELECT * FROM teams')
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
    assert teams_after_creation[0]['segment'] == segment
    # update
    assert update_response['success'] is True
    assert update_response['message'] == 'Информация про команду была успешно обновлена.'
    assert len(teams_after_update) == 1
    assert teams_after_update[0]['team_id'] == team_id
    assert teams_after_update[0]['lead_id'] == new_lead_id
    assert teams_after_update[0]['team_name'] == new_name
    assert teams_after_update[0]['segment'] == new_segment
    # delete
    assert delete_response['success'] is True
    assert delete_response['message'] == 'Команда была успешно удалена.'
    assert len(teams_after_deletion) == 0


# # render teams.jinja2


async def test_render_teams(
    pg, http, users_mock,
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


@pytest.mark.html
async def test_render_team_card(http, pg):
    # arrange
    user_id = 100
    name = 'Команда'
    lead_id = '1'
    segment = 'c'
    await http.request(
        'POST',
        '/api/admin/v1/create-team-public/',
        json={
            'teamName': name,
            'leadId': lead_id,
            'segment': segment,
        },
        headers={
            'X-Real-UserId': user_id,
        },
        expected_status=200
    )
    team_id = await pg.fetchval('SELECT team_id FROM teams LIMIT 1')
    # act
    resp = await http.request(
        'GET',
        f'/admin/team-card/{team_id}/',
        headers={
            'X-Real-UserId': user_id,
        },
        expected_status=200
    )

    html = resp.body.decode('utf-8')
    # assert
    assert html is not None
