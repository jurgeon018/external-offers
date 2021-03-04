import pytest
from cian_test_utils import future

from external_offers.entities import Client, ReturnClientByPhoneRequest
from external_offers.enums import ClientStatus, ReturnClientByPhoneErrorCode
from external_offers.services.return_client_by_phone import return_client_by_phone


async def test_return_client_by_phone__missing_client_status__return_error(mocker):
    # arrange
    get_client_for_update_by_phone_number_mock = mocker.patch('external_offers.services.return_client_by_phone.'
                                                              'get_client_for_update_by_phone_number')

    get_client_for_update_by_phone_number_mock.return_value = future(
        None
    )

    # act
    res = await return_client_by_phone(
        request=ReturnClientByPhoneRequest(
            phone_number='89111111111'
        ),
        user_id=mocker.sentinel.user_id
    )

    # assert
    assert res.errors[0].code == ReturnClientByPhoneErrorCode.missing_client


@pytest.mark.parametrize(('status'), (
    ClientStatus.in_progress,
    ClientStatus.declined,
    ClientStatus.accepted,
))
async def test_return_client_by_phone__unsuitable_client_status__return_error(mocker, status):
    # arrange
    get_client_for_update_by_phone_number_mock = mocker.patch('external_offers.services.return_client_by_phone.'
                                                              'get_client_for_update_by_phone_number')

    client = Client(
        client_id='1',
        avito_user_id=1,
        client_phones=['89111111111'],
        status=status
    )
    get_client_for_update_by_phone_number_mock.return_value = future(client)

    # act
    res = await return_client_by_phone(
        request=ReturnClientByPhoneRequest(
            phone_number='89111111111'
        ),
        user_id=mocker.sentinel.user_id
    )

    # assert
    assert res.errors[0].code == ReturnClientByPhoneErrorCode.wrong_status


@pytest.mark.parametrize(('request_phone'), (
    '79111111111',
    '89111111111',
    '+79111111111'
))
async def test_return_client_by_phone__wrong_format_phone__called_with_transformed(mocker, request_phone):
    # arrange
    get_client_for_update_by_phone_number_mock = mocker.patch('external_offers.services.return_client_by_phone.'
                                                              'get_client_for_update_by_phone_number')

    get_client_for_update_by_phone_number_mock.return_value = future(None)

    # act
    await return_client_by_phone(
        request=ReturnClientByPhoneRequest(
            phone_number=request_phone
        ),
        user_id=mocker.sentinel.user_id
    )

    # assert
    get_client_for_update_by_phone_number_mock.assert_called_with(
        phone_number='89111111111'
    )
