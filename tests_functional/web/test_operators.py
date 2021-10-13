import json

import pytest


async def test_operators(pg, http):
    # arrange
    operator_id = '123'
    name = 'operator'
    team_id = 5
    new_name = 'new operator'
    new_team_id = 6
    # act
    # create
    create_response = await http.request(
        'POST',
        '/api/admin/v1/create-operator-public/',
        json={
            'operatorId': operator_id,
            'fullName': name,
            'teamId': team_id,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    create_response = json.loads(create_response.body.decode('utf-8'))
    operators_after_creation = await pg.fetch('SELECT * FROM operators')
    # update
    update_response = await http.request(
        'POST',
        '/api/admin/v1/update-operator-public/',
        json={
            'operatorId': operator_id,
            'fullName': new_name,
            'teamId': new_team_id,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    update_response = json.loads(update_response.body.decode('utf-8'))
    operators_after_update = await pg.fetch('SELECT * FROM operators')
    # delete
    delete_response = await http.request(
        'POST',
        '/api/admin/v1/delete-operator-public/',
        json={
            'operatorId': operator_id,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    delete_response = json.loads(delete_response.body.decode('utf-8'))
    operators_after_deletion = await pg.fetch('SELECT * FROM operators')
    # assert
    # create
    assert create_response['message'] == 'Оператор был успешно создан.'
    assert create_response['success'] is True
    assert len(operators_after_creation) == 1
    assert operators_after_creation[0]['operator_id'] == operator_id
    assert operators_after_creation[0]['full_name'] == name
    assert operators_after_creation[0]['team_id'] == team_id
    # update
    assert update_response['message'] == 'Информация про оператора была успешно обновлена.'
    assert update_response['success'] is True
    assert len(operators_after_update) == 1
    assert operators_after_update[0]['operator_id'] == operator_id
    assert operators_after_update[0]['full_name'] == new_name
    assert operators_after_update[0]['team_id'] == new_team_id
    # delete
    assert delete_response['message'] == 'Оператор был успешно удален.'
    assert delete_response['success'] is True
    assert len(operators_after_deletion) == 0


@pytest.mark.html
async def test_render_operator_card(http, pg):
    # arrange
    user_id = 100
    operator_id = '1'
    name = 'Оператор'
    team_id = '1'
    await http.request(
        'POST',
        '/api/admin/v1/create-operator-public/',
        json={
            'operatorId': operator_id,
            'fullName': name,
            'teamId': team_id,
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )
    # act
    resp = await http.request(
        'GET',
        f'/admin/operator-card/{operator_id}/',
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )

    html = resp.body.decode('utf-8')
    # assert
    assert html is not None
