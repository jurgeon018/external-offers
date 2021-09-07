import pytest
import json
from unittest.mock import MagicMock
from cian_test_utils import future


@pytest.mark.gen_test
async def test_create_team(http_client, base_url, mocker):
    # arrange
    name = None
    lead_id = None
    segment = None
    settings = None
    # act
    result = await http_client.fetch(
        base_url+'/api/admin/v1/create-team-public/',
        method='POST',
        body=json.dumps({
            'name': name,
            'leadId': lead_id,
            'segment': segment,
            'settings': settings,
        }),
        headers={
            'X-Real-UserId': '1',
        },
    )
    # assert


@pytest.mark.gen_test
async def test_update_team(http_client, base_url, mocker):
    pass


@pytest.mark.gen_test
async def test_delete_team(http_client, base_url, mocker):
    pass
