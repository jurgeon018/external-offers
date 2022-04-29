import json

import pytest
from cian_test_utils import future

from external_offers.entities.clients import Client
from external_offers.enums.client_status import ClientStatus


@pytest.mark.gen_test
async def test_update_client_real_info(http_client, base_url, mocker):
    # arrange
    get_client_by_client_id_mock = mocker.patch(
        'external_offers.services.update_client_real_info.get_client_by_client_id'
    )
    get_client_by_client_id_mock.return_value = future(0)
    client_id = '1'
    real_phone = '8 800 555 35 35'
    real_phone_hunted_at = '2022-01-14 04:44:44.794400+00:00'
    real_name = 'Реальное ФИО'
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/update-client-real-info/',
        method='POST',
        body=json.dumps({
            'clientId': client_id,
            'realPhone': real_phone,
            'realPhone_hunted_at': real_phone_hunted_at,
            'realName': real_name,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    data = json.loads(result.body)
    # assert
    assert data['success'] is False
    assert data['message'] == 'Пользователь с переданным идентификатором не найден'


@pytest.mark.gen_test
async def test_return_waiting_client_to_waiting_public(http_client, base_url, mocker):
    # arrange
    client_id = '1'
    real_phone = '8 800 555 35 35'
    real_phone_hunted_at = '2022-01-14 04:44:44.794400+00:00'
    real_name = 'Реальное ФИО'
    get_client_by_client_id_mock = mocker.patch(
        'external_offers.services.admin.get_client_by_client_id',
        return_value=future(Client(
            client_id=client_id,
            avito_user_id='12345',
            client_phones=[],
            status=ClientStatus.in_progress,
            real_name=real_name,
            real_phone_hunted_at=real_phone_hunted_at,
            real_phone=real_phone,
        ))
    )
    return_client_to_waiting_by_client_id_mock = mocker.patch(
        'external_offers.services.admin.return_client_to_waiting_by_client_id',
        return_value=future(None),
    )
    return_offers_to_waiting_by_client_id_mock = mocker.patch(
        'external_offers.services.admin.return_offers_to_waiting_by_client_id',
        return_value=future(None),
    )
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/return-client-to-waiting/',
        method='POST',
        body=json.dumps({
            'clientId': client_id,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    data = json.loads(result.body)
    # assert
    assert data['message'] == 'Клиент был успешно возвращен в очередь на прозвон.'
    assert data['success'] is True
    get_client_by_client_id_mock.assert_called_once()
    return_client_to_waiting_by_client_id_mock.assert_called_once()
    return_offers_to_waiting_by_client_id_mock.assert_called_once()
