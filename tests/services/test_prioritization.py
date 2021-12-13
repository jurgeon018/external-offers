from cian_test_utils import future

from external_offers.entities.clients import Client, ClientStatus
from external_offers.repositories.users.entities.user_model_v2 import UserModelV2
from external_offers.services.prioritizers.prioritize_homeowner import (
    _CLEAR_CLIENT_PRIORITY,
    GetUsersByPhoneResponseV2,
    find_homeowner_client_account_priority,
)


async def test__find_homeowner_client_account_priority__clear_homeowners_with_existing_accounts(
    mocker,
    fake_settings
):
    # arrange
    await fake_settings.set(
        CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS=True
    )
    mocker.patch(
        'external_offers.services.prioritizers.prioritize_homeowner.v2_get_users_by_phone',
        return_value=future(GetUsersByPhoneResponseV2(
            users=[
                UserModelV2()
            ]
        ))
    )
    client = Client(
        cian_user_id=None,
        client_id=12345,
        avito_user_id=23456,
        client_phones=['88005553535'],
        status=ClientStatus.waiting,
    )
    # act
    team_settings = {
        'no_lk_homeowner_priority': 1,
        'active_lk_homeowner_priority': 2,
    }
    result = await find_homeowner_client_account_priority(
        client=client,
        team_settings=team_settings,
        client_account_statuses=None,
    )
    # assert
    assert result == _CLEAR_CLIENT_PRIORITY
