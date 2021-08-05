import json

import pytest
from cian_test_utils import future

from external_offers.enums.client_status import ClientStatus
from external_offers.services.test_objects import (
    Client,
    CreateTestClientRequest,
    CreateTestClientResponse,
    CreateTestOfferRequest,
    CreateTestOfferResponse,
    create_test_client_public,
    create_test_offer_public,
    get_attr,
)


# get_attr

def test_get_attr__invalid_object_instance_passed__raises_exception():
    with pytest.raises(Exception) as e:
        get_attr(None, 'attribute')
    assert str(e.value) == 'Invalid request instance'


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


# create_test_client


@pytest.mark.gen_test
async def test_create_test_client_public__client_exists__returns_client_id(
    http_client, base_url, mocker
):
    # arrange
    client_id = '442'
    client = Client(
        client_id=client_id,
        avito_user_id='1',
        client_phones=['1'],
        status=ClientStatus.waiting,
    )
    source_user_id = '3421'
    get_client_by_avito_user_id_mock = mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value = future(client),
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


@pytest.mark.gen_test
async def test_create_test_client_public__invalid_json__returns_error_message(
    http_client, base_url, mocker
):
    # arrange
    source_user_id = '3421'
    mocker.patch(
        'external_offers.services.test_objects.get_client_by_avito_user_id',
        return_value = future(None),
    )
    mocker.patch(
        'external_offers.services.test_objects.get_default_test_client',
        return_value = future('invalid json'),
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


async def test_create_test_client_public3(
    http_client, base_url, mocker
):
    pass


async def test_create_test_client_public4(
    http_client, base_url, mocker
):
    pass


# create_test_offer

async def test_create_test_offer_public1(
    http_client, base_url, mocker
):
    pass


async def test_create_test_offer_public2(
    http_client, base_url, mocker
):
    pass


async def test_create_test_offer_public3(
    http_client, base_url, mocker
):
    pass


async def test_create_test_offer_public4(
    http_client, base_url, mocker
):
    pass


async def test_create_test_offer_public5(
    http_client, base_url, mocker
):
    pass


async def test_create_test_offer_public6(
    http_client, base_url, mocker
):
    pass


async def test_create_test_offer_public7(
    http_client, base_url, mocker
):
    pass


async def test_create_test_offer_public8(
    http_client, base_url, mocker
):
    pass
