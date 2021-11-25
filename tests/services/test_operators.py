import json

import pytest
from asyncpg.exceptions import PostgresError, UniqueViolationError
from cian_test_utils import future


# test_create_operator


@pytest.mark.gen_test
async def test_create_operator__success_is_true(http_client, base_url, mocker):
    # arrange
    mocker.patch(
        'external_offers.services.operators.create_operator',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.services.operator_roles.v1_add_role_to_user',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.services.operators.update_operators',
        return_value=future(None),
    )
    
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-operator-public/',
        method='POST',
        body=json.dumps({
            'operatorId': '123',
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['message'] == 'Оператор был успешно создан.'
    assert body['success'] is True


@pytest.mark.gen_test
async def test_create_operator__unique_violation_error(http_client, base_url, mocker):
    # arrange
    msg = 'error'
    mocker.patch(
        'external_offers.services.operators.create_operator',
        side_effect=UniqueViolationError(msg),
    )
    mocker.patch(
        'external_offers.services.operator_roles.v1_add_role_to_user',
        return_value=future(None),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-operator-public/',
        method='POST',
        body=json.dumps({
            'operatorId': '123',
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is False
    assert body['message'] == f'Такой оператор уже существует: {msg}'


@pytest.mark.gen_test
async def test_create_operator__postgres_error(http_client, base_url, mocker):
    # arrange
    msg = 'error'
    mocker.patch(
        'external_offers.services.operators.create_operator',
        side_effect=PostgresError(msg),
    )
    mocker.patch(
        'external_offers.services.operator_roles.v1_add_role_to_user',
        return_value=future(None),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-operator-public/',
        method='POST',
        body=json.dumps({
            'operatorId': '123',
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is False
    assert body['message'] == f'Во время создания оператора произошла ошибка: {msg}'


# test_update_operator


@pytest.mark.gen_test
async def test_update_operator__success_is_true(http_client, base_url, mocker):
    # arrange
    mocker.patch(
        'external_offers.services.operators.update_operator_by_id',
        return_value=future(None),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/update-operator-public/',
        method='POST',
        body=json.dumps({
            'operatorId': '1',
            'fullName': 'name',
            'teamId': '1',
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is True
    assert body['message'] == 'Информация про оператора была успешно обновлена.'


@pytest.mark.gen_test
async def test_update_operator__postgres_error(http_client, base_url, mocker):
    # arrange
    msg = 'error'
    mocker.patch(
        'external_offers.services.operators.update_operator_by_id',
        side_effect=PostgresError(msg),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/update-operator-public/',
        method='POST',
        body=json.dumps({
            'operatorId': '1',
            'fullName': 'name',
            'teamId': '1',
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is False
    assert body['message'] == f'Во время обновления оператора произошла ошибка: {msg}'


# test_delete_operator


@pytest.mark.gen_test
async def test_delete_operator__success_is_true(http_client, base_url, mocker):
    # arrange
    mocker.patch(
        'external_offers.services.operators.delete_operator_by_id',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.services.operator_roles.v1_remove_role_from_user',
        return_value=future(None),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/delete-operator-public/',
        method='POST',
        body=json.dumps({
            'operatorId': '1',
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is True
    assert body['message'] == 'Оператор был успешно удален.'


@pytest.mark.gen_test
async def test_delete_operator__postgres_error(http_client, base_url, mocker):
    # arrange
    msg = 'error'
    mocker.patch(
        'external_offers.services.operators.delete_operator_by_id',
        side_effect=PostgresError(msg),
    )
    mocker.patch(
        'external_offers.services.operator_roles.v1_remove_role_from_user',
        return_value=future(None),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/delete-operator-public/',
        method='POST',
        body=json.dumps({
            'operatorId': '1',
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    body = json.loads(result.body)
    # assert
    assert body['success'] is False
    assert body['message'] == f'Во время удаления оператора произошла ошибка: {msg}'
