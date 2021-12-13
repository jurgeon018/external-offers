import json

import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_operators(pg, http, users_mock):
    # arrange
    operator_id = '3'
    new_name = 'new operator'
    new_team_id = 6
    await users_mock.add_stub(
        method='POST',
        path='/v1/add-role-to-user/',
        response=MockResponse(
            body=None
        ),
    )
    await users_mock.add_stub(
        method='POST',
        path='/v1/remove-role-from-user/',
        response=MockResponse(
            body=None
        ),
    )
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-userids-by-rolename/',
        response=MockResponse(
            body={
                'userIds': [1, 2, 3, 4],
            }
        ),
    )
    await users_mock.add_stub(
        method='POST',
        path='/v1/get-users/',
        response=MockResponse(
            body={
                'users': [
                    {
                        'user_name': 'Юзер1',
                        'email': 'email1@cian.ru',
                    },
                    {
                        'id': '2',
                        'user_name': 'Юзер2',
                        'email': 'email2@cian.ru',
                    },
                    {
                        'id': '3',
                        'first_name': 'Юзер',
                        'last_name': '3',
                        'email': 'email3@cian.ru',
                    },
                    {
                        'id': '4',
                    },
                ],
            }
        ),
    )
    await users_mock.add_stub(
        method='GET',
        path='/v1/user-has-role/',
        response=MockResponse(
            body=True,
        ),
    )
    # act
    # create
    create_response = await http.request(
        'POST',
        '/api/admin/v1/create-operator-public/',
        json={
            'operatorId': operator_id,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    create_response = json.loads(create_response.body.decode('utf-8'))
    operators_after_creation = await pg.fetch('SELECT * FROM operators')
    operator_after_creation = await pg.fetchrow('SELECT * FROM operators where operator_id=$1', [operator_id])
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
    operator_after_update = await pg.fetchrow('SELECT * FROM operators WHERE operator_id=$1', [operator_id])

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
    assert len(operators_after_creation) == 3
    assert operator_after_creation['operator_id'] == operator_id
    assert operator_after_creation['full_name'] == 'Юзер 3'
    assert operator_after_creation['team_id'] is None
    # update
    assert update_response['message'] == 'Информация про оператора была успешно обновлена.'
    assert update_response['success'] is True
    assert len(operators_after_update) == 3
    assert operator_after_update['operator_id'] == operator_id
    assert operator_after_update['full_name'] == new_name
    assert operator_after_update['team_id'] == new_team_id
    # delete
    assert delete_response['message'] == 'Оператор был успешно удален.'
    assert delete_response['success'] is True
    assert len(operators_after_deletion) == 2


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


@pytest.mark.html
async def test_update_operators_public(
    http, pg, users_mock,
    runtime_settings,
):
    # arrange
    user_id = 100
    await runtime_settings.set({
        'ADMIN_OPERATOR_ROLE': 'Cian.PrepositionAdmin',
        'ADMIN_TEAMLEAD_ROLE': 'Cian.PrepositionAdminTeamlead',
    })
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-userids-by-rolename/',
        response=MockResponse(
            body={
                'userIds': [1, 2, 3, 4],
            }
        ),
    )
    await users_mock.add_stub(
        method='POST',
        path='/v1/get-users/',
        response=MockResponse(
            body={
                'users': [
                    {
                        'user_name': 'Юзер1',
                        'email': 'email1@cian.ru',
                    },
                    {
                        'id': '2',
                        'user_name': 'Юзер2',
                        'email': 'email2@cian.ru',
                    },
                    {
                        'id': '3',
                        'first_name': 'Юзер',
                        'last_name': '3',
                        'email': 'email3@cian.ru',
                    },
                    {
                        'id': '4',
                    },
                ],
            }
        ),
    )
    await users_mock.add_stub(
        method='GET',
        path='/v1/user-has-role/',
        response=MockResponse(
            body=True,
        ),
    )
    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-operators-public/',
        json={},
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )
    response = json.loads(resp.body.decode('utf-8'))
    operators = await pg.fetch("""
    select * from operators
    """)
    # assert
    assert response['success'] is True
    assert len(operators) == 3

    assert operators[0]['operator_id'] == '2'
    assert operators[0]['email'] == 'email2@cian.ru'
    assert operators[0]['full_name'] == 'Юзер2'
    assert operators[0]['is_teamlead'] is True

    assert operators[1]['operator_id'] == '3'
    assert operators[1]['email'] == 'email3@cian.ru'
    assert operators[1]['full_name'] == 'Юзер 3'
    assert operators[1]['is_teamlead'] is True

    assert operators[2]['operator_id'] == '4'
    assert operators[2]['email'] is None
    assert operators[2]['full_name'] is None
    assert operators[2]['is_teamlead'] is True
