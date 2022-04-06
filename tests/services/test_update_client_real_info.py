import json

import pytest
from cian_test_utils import future


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
