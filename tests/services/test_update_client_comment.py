import json
from cian_test_utils import future
import pytest


@pytest.mark.gen_test
async def test_update_client_comment__(http_client, base_url, mocker):
    
    
    get_client_by_client_id_mock = mocker.patch('external_offers.services.update_client_comment.get_client_by_client_id')
    get_client_by_client_id_mock.return_value = future(1)
    set_comment_by_client_id_mock = mocker.patch('external_offers.services.update_client_comment.set_comment_by_client_id')
    set_comment_by_client_id_mock.side_effect = Exception('error')
    set_comment_by_client_id_mock.return_value = future(None)

    client_id = '1'
    comment = 'comment text'
    result = await http_client.fetch(
        base_url+'/api/admin/v1/update-client-comment/',
        method='POST',
        body=json.dumps({
            'clientId': client_id,
            'comment': comment,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    data = json.loads(result.body)
    assert data['success'] is False
    assert data['message'] == 'Ошибка при обновлении коментария. error'
