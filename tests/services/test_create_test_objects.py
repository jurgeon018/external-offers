import json

import pytest
from asyncpg.exceptions import PostgresError
from cian_test_utils import future

from external_offers.enums.client_status import ClientStatus
from external_offers.repositories.postgresql.parsed_offers import ParsedOfferForCreation
from external_offers.services.test_objects import Client, CreateTestClientRequest, CreateTestOfferRequest, get_attr


# get_attr
def test_get_attr__invalid_object_instance_passed__raises_exception():
    with pytest.raises(Exception) as err:
        get_attr(None, 'attribute')
    assert str(err.value) == 'Invalid request instance'


def test_get_attr__dict_passed__returns_value():
    attr = get_attr({'client_name': 'value'}, 'client_name')
    assert attr == 'value'


def test_get_attr__client_request_passed__returns_value():
    client_name = 'value'
    client_request = CreateTestClientRequest(
        use_default=False,
        source_user_id='1',
        client_name=client_name,
    )
    attr = get_attr(client_request, 'client_name')
    assert attr == client_name


def test_get_attr__offer_request_passed__returns_value():
    user_segment = 'c'
    offer_request = CreateTestOfferRequest(
        use_default=False,
        source_object_id='1',
        user_segment=user_segment
    )
    attr = get_attr(offer_request, 'user_segment')
    assert attr == user_segment


# create_test_parsed_offer


@pytest.mark.gen_test
async def test_create_test_parsed_offer__client_exists(
    http_client, base_url, mocker
):
    # arrange
    client_id = '442'
    source_user_id = '3421'
    client = Client(
        client_id=client_id,
        avito_user_id=source_user_id,
        client_phones=['123'],
        status=ClientStatus.waiting,
    )
    get_client_by_avito_user_id_mock = mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(client),
    )
    check_cian_user_id_mock = mocker.patch(
        'external_offers.services.test_objects.check_cian_user_id',
        return_value=future(False),
    )
    # act
    result = await http_client.fetch(
        base_url+'/qa/v1/create-test-parsed-offer/',
        method='POST',
        body=json.dumps({
            'sourceObjectId': '123',
            'sourceUserId': source_user_id,
            'isCalltracking': False,
            'userSegment': 'c',
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == f'Клиент с sourceUserId {source_user_id} уже существует. Выберите другой sourceUserId.'
    get_client_by_avito_user_id_mock.assert_called_once_with(avito_user_id=source_user_id)
    check_cian_user_id_mock.assert_not_called()


@pytest.mark.gen_test
async def test_create_test_parsed_offer__parsed_offer_exists(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '3421'
    source_object_id = '123'
    get_client_by_avito_user_id_mock = mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(None),
    )
    exists_parsed_offer_by_source_object_id_mock = mocker.patch(
        'external_offers.services.test_objects.exists_parsed_offer_by_source_object_id',
        return_value=future(True)
    )
    check_cian_user_id_mock = mocker.patch(
        'external_offers.services.test_objects.check_cian_user_id',
        return_value=future(False),
    )
    # act
    result = await http_client.fetch(
        base_url+'/qa/v1/create-test-parsed-offer/',
        method='POST',
        body=json.dumps({
            'sourceObjectId': source_object_id,
            'sourceUserId': source_user_id,
            'isCalltracking': False,
            'userSegment': 'c',
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == f'Обьявление с source_object_id {source_object_id} уже существует.'
    get_client_by_avito_user_id_mock.assert_called_once_with(avito_user_id=source_user_id)
    check_cian_user_id_mock.assert_not_called()
    exists_parsed_offer_by_source_object_id_mock.assert_called_once_with(source_object_id=source_object_id)


# create_test_client
@pytest.mark.gen_test
async def test_create_test_client_public__client_exists__returns_client_id(
    http_client, base_url, mocker
):
    # arrange
    client_id = '442'
    source_user_id = '3421'
    client = Client(
        client_id=client_id,
        avito_user_id=source_user_id,
        client_phones=['123'],
        status=ClientStatus.waiting,
    )
    get_client_by_avito_user_id_mock = mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(client),
    )
    check_cian_user_id_mock = mocker.patch(
        'external_offers.services.test_objects.check_cian_user_id',
        return_value=future(False),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-client/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceUserId': source_user_id,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is True
    assert data['message'] == f'Клиент с source_user_id {source_user_id} уже существует.'
    assert data['clientId'] == client_id
    get_client_by_avito_user_id_mock.assert_called_once_with(avito_user_id=source_user_id)
    check_cian_user_id_mock.assert_not_called()


@pytest.mark.gen_test
async def test_create_test_client_public__invalid_json__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '3421'
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.services.test_objects.get_default_test_client',
        return_value=future('invalid json'),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-client/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceUserId': source_user_id,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert 'Невалидное значение в переменной DEFAULT_TEST_CLIENT.' in data['message']


@pytest.mark.gen_test
async def test_create_test_client_public__error_while_saving__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '3421'
    error = 'error message'
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.services.test_objects.save_client',
        return_value=future(None),
        side_effect=PostgresError(error),
    )

    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-client/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceUserId': source_user_id,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == f'Не удалось создать клиента из-за ошибки: {error}'


@pytest.mark.gen_test
async def test_create_test_client_public__no_errors__returns_success_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '3421'
    client_id = '1234'
    cian_user_id = 123
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.services.test_objects.generate_guid',
        return_value=client_id,
    )
    mocker.patch(
        'external_offers.services.test_objects.check_cian_user_id',
        return_value=future(False),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-client/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceUserId': source_user_id,
            'cianUserId': cian_user_id
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is True
    assert data['message'] == 'Тестовый клиент был успешно создан.'
    assert data['clientId'] == client_id


@pytest.mark.gen_test
async def test_create_test_client_public__cian_user_id_exists__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '3421'
    client_id = '1234'
    cian_user_id = 123

    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.services.test_objects.generate_guid',
        return_value=client_id,
    )
    mocker.patch(
        'external_offers.services.test_objects.check_cian_user_id',
        return_value=future(True),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-client/',
        method='POST',
        body=json.dumps({
            'useDefault': False,
            'sourceUserId': source_user_id,
            'cianUserId': cian_user_id
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == f'Клиент с таким cian_user_id: {cian_user_id} уже существует'


# create_test_offer
@pytest.mark.gen_test
async def test_create_test_offer_public__no_client_with_source_user_id__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '123123'
    source_object_id = '1_123123'
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(None)
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-offer/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceUserId': source_user_id,
            'sourceObjectId': source_object_id,
        }),
        headers={
          'X-Real-UserId': '1',
        }
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == f'Клиент с sourceUserId {source_user_id} не существует. Сначала создайте клиента.'


@pytest.mark.gen_test
async def test_create_test_offer_public__no_client_with_client_id__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_client_id',
        return_value=future(None)
    )
    client_id = '123123'
    source_object_id = '1_123123'
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-offer/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'clientId': client_id,
            'sourceObjectId': source_object_id,
        }),
        headers={
          'X-Real-UserId': '1',
        }
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == f'Клиент с clientId {client_id} не существует. Сначала создайте клиента.'


@pytest.mark.gen_test
async def test_create_test_offer_public__invalid_request__returns_error_message(
    http_client, base_url
):
    # arrange
    source_object_id = '1_123123'
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-offer/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceObjectId': source_object_id,
        }),
        headers={
          'X-Real-UserId': '1',
        }
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == 'Отправьте clientId либо sourceUserId.'


@pytest.mark.gen_test
async def test_create_test_offer_public__offer_exists__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(mocker.MagicMock())
    )
    mocker.patch(
        'external_offers.services.test_objects.exists_parsed_offer_by_source_object_id',
        return_value=future(True)
    )
    source_object_id = '1_123123'
    source_user_id = '111'
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-offer/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceObjectId': source_object_id,
            'sourceUserId': source_user_id
        }),
        headers={
          'X-Real-UserId': '1',
        }
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == f'Обьявление с source_object_id {source_object_id} уже существует.'


@pytest.mark.gen_test
async def test_create_test_offer_public__json_error__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '123123'
    source_object_id = '1_123123'
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(mocker.MagicMock())
    )
    mocker.patch(
        'external_offers.services.test_objects.exists_parsed_offer_by_source_object_id',
        return_value=future(False)
    )
    mocker.patch(
        'external_offers.services.test_objects.get_default_test_offer',
        return_value=future('invalid json')
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-offer/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceUserId': source_user_id,
            'sourceObjectId': source_object_id,
        }),
        headers={
          'X-Real-UserId': '1',
        }
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert 'Невалидное значение в переменной DEFAULT_TEST_OFFER.' in data['message']


@pytest.mark.gen_test
async def test_create_test_offer_public__parsed_offer_postgres_error__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '123123'
    source_object_id = '1_123123'
    err = 'error message'
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(mocker.MagicMock())
    )
    mocker.patch(
        'external_offers.services.test_objects.exists_parsed_offer_by_source_object_id',
        return_value=future(False)
    )
    mocker.patch(
        'external_offers.services.test_objects.save_test_parsed_offer',
        return_value=future(None),
        side_effect=PostgresError(err)
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-offer/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceUserId': source_user_id,
            'sourceObjectId': source_object_id,
        }),
        headers={
          'X-Real-UserId': '1',
        }
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == f'Не удалось создать спаршеное обьявление из-за ошибки: {err}'


@pytest.mark.gen_test
async def test_create_test_offer_public__offer_postgres_error__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '123123'
    source_object_id = '1_123123'
    offer_id = '321321231'
    err = 'error message'
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(mocker.MagicMock())
    )
    mocker.patch(
        'external_offers.services.test_objects.exists_parsed_offer_by_source_object_id',
        return_value=future(False)
    )
    mocker.patch(
        'external_offers.services.test_objects.generate_guid',
        return_value=offer_id
    )
    mocker.patch(
        'external_offers.services.test_objects.get_parsed_offer_for_creation_by_id',
        return_value=future(mocker.MagicMock())
    )
    mocker.patch(
        'external_offers.services.test_objects.save_offer_for_call',
        return_value=future(None),
        side_effect=PostgresError(err)
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-offer/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceUserId': source_user_id,
            'sourceObjectId': source_object_id,
        }),
        headers={
          'X-Real-UserId': '1',
        }
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == f'Не удалось создать задание из-за ошибки: {err}'


@pytest.mark.gen_test
async def test_create_test_offer_public__no_errors__returns_success_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '123123'
    source_object_id = '1_123123'
    offer_id = '321321231'
    client = Client(
        client_id='123',
        avito_user_id='123',
        client_phones=['123'],
        status=ClientStatus.waiting,
    )
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value=future(client)
    )
    mocker.patch(
        'external_offers.services.test_objects.exists_parsed_offer_by_source_object_id',
        return_value=future(False)
    )
    mocker.patch(
        'external_offers.services.test_objects.generate_guid',
        return_value=offer_id
    )
    parsed_offer_for_creation = ParsedOfferForCreation(
        id='123',
        timestamp='..',
        created_at='..',
        contact='contact',
        source_user_id=source_user_id,
        phones=['1111'],
        user_segment='c',
        category='flatSale',
        user_subsegment='subsegment1',
        source_group_id='groupid1',
    )
    mocker.patch(
        'external_offers.services.test_objects.get_parsed_offer_for_creation_by_id',
        return_value=future(parsed_offer_for_creation)
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-test-offer/',
        method='POST',
        body=json.dumps({
            'useDefault': True,
            'sourceUserId': source_user_id,
            'sourceObjectId': source_object_id,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    # assert
    data = json.loads(result.body)
    assert data['success'] is True
    assert data['message'] == 'Тестовое обьявление было успешно создано.'
    assert data['offerId'] == offer_id
