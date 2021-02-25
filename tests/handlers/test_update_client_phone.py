import json

import pytest
from cian_test_utils import future


@pytest.mark.gen_test
async def test_update_client_phone__missing_client__return_error(http_client, base_url, mocker):
    # arrange
    client_id = '1'
    phone_number = '+79819421122'
    get_client_by_client_id_mock = mocker.patch('external_offers.services.update_client_phone'
                                      '.get_client_by_client_id')
    get_client_by_client_id_mock.return_value = future(None)

    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/update-client-phone/',
        method='POST',
        body=json.dumps({
            'clientId': client_id,
            'phoneNumber': phone_number
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    data = json.loads(result.body)

    # assert
    assert data['errors'][0]['code'] == 'missingClient'
    assert not data['success']
