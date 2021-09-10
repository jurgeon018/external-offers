import pytest
import json
from cian_test_utils import future
from asyncpg.exceptions import PostgresError, UniqueViolationError


# test_create_team


@pytest.mark.gen_test
async def test_create_team__success_is_true(http_client, base_url, mocker):
    # arrange
    mocker.patch(
        'external_offers.services.teams.create_team',
        return_value=future(None),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-team-public/',
        method='POST',
        body=json.dumps({
            'name': "name",
            'leadId': "1",
            'segment': "c",
            'settings': None,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is True
    assert body['message'] == 'Команда была успешно создана.'


@pytest.mark.gen_test
async def test_create_team__unique_violation_error(http_client, base_url, mocker):
    # arrange
    msg = 'error'
    mocker.patch(
        'external_offers.services.teams.create_team',
        side_effect=UniqueViolationError(msg),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-team-public/',
        method='POST',
        body=json.dumps({
            'name': "name",
            'leadId': "1",
            'segment': "c",
            'settings': None,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is False
    assert body['message'] == f'Такая команда уже существует: {msg}'


@pytest.mark.gen_test
async def test_create_team__postgres_error(http_client, base_url, mocker):
    # arrange
    msg = 'error'
    mocker.patch(
        'external_offers.services.teams.create_team',
        side_effect=PostgresError(msg),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-team-public/',
        method='POST',
        body=json.dumps({
            'name': "name",
            'leadId': "1",
            'segment': "c",
            'settings': None,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is False
    assert body['message'] == f'Во время создания команды произошла ошибка: {msg}'


# test_update_team


@pytest.mark.gen_test
async def test_update_team__success_is_true(http_client, base_url, mocker):
    # arrange
    mocker.patch(
        'external_offers.services.teams.update_team_by_id',
        return_value=future(None),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/update-team-public/',
        method='POST',
        body=json.dumps({
            'id': "1",
            'name': "name",
            'leadId': "1",
            'segment': "c",
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is True
    assert body['message'] == 'Информация про команду была успешно обновлена.'



@pytest.mark.gen_test
async def test_update_team__postgres_error(http_client, base_url, mocker):
    # arrange
    msg = 'error'
    mocker.patch(
        'external_offers.services.teams.update_team_by_id',
        side_effect=PostgresError(msg),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/update-team-public/',
        method='POST',
        body=json.dumps({
            'id': "1",
            'name': "name",
            'leadId': "1",
            'segment': "c",
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is False
    assert body['message'] == f'Во время обновления команды произошла ошибка: {msg}'


# test_delete_team


@pytest.mark.gen_test
async def test_delete_team__success_is_true(http_client, base_url, mocker):
    # arrange
    mocker.patch(
        'external_offers.services.teams.delete_team_by_id',
        return_value=future(None),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/delete-team-public/',
        method='POST',
        body=json.dumps({
            'id': "1",
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is True
    assert body['message'] == 'Команда была успешно удалена.'


@pytest.mark.gen_test
async def test_delete_team__postgres_error(http_client, base_url, mocker):
    # arrange
    msg = 'error'
    mocker.patch(
        'external_offers.services.teams.delete_team_by_id',
        side_effect=PostgresError(msg),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/delete-team-public/',
        method='POST',
        body=json.dumps({
            'id': "1",
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is False
    assert body['message'] == f'Во время удаления команды произошла ошибка: {msg}'

