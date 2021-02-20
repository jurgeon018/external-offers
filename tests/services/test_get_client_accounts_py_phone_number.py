from cian_test_utils import future

from external_offers.entities.clients import ClientAccountInfo
from external_offers.repositories.users.entities.get_users_by_phone_response_v2 import (
    GetUsersByPhoneResponseV2,
    UserModelV2,
)
from external_offers.repositories.users.entities.user_model_v2 import ExternalUserSourceType, State
from external_offers.repositories.users.entities.v2_get_users_by_phone import V2GetUsersByPhone
from external_offers.services.accounts.client_accounts import get_client_accounts_by_phone_number


async def test_get_client_accounts_by_phone_number__called_with_phone__returns_correct_accounts(mocker):
    # arrange
    test_phone = 'test'
    v2_get_users_by_phone_mock = mocker.patch('external_offers.services.accounts.client_accounts.v2_get_users_by_phone')
    v2_get_users_by_phone_mock.return_value = future(GetUsersByPhoneResponseV2(
        users=[
            UserModelV2(
                cian_user_id=1,
                is_agent=True,
                state=State.active,
                external_user_source_type=ExternalUserSourceType.sub_agents
            ),
            UserModelV2(
                cian_user_id=2,
                is_agent=True,
                state=State.active,
                external_user_source_type=ExternalUserSourceType.emls
            ),
            UserModelV2(
                cian_user_id=3,
                is_agent=False,
                state=State.blocked
            ),
            UserModelV2(
                cian_user_id=4,
                is_agent=False,
                state=State.deleted
            ),
            UserModelV2(
                cian_user_id=5,
                is_agent=True,
                state=State.active,
                email='test5@cian.ru'
            ),
            UserModelV2(
                cian_user_id=6,
                is_agent=False,
                state=State.blocked
            ),
            UserModelV2(
                cian_user_id=7,
                is_agent=False,
                state=State.active,
                email='test7@cian.ru'
            )
        ]
    ))

    # act
    result = await get_client_accounts_by_phone_number(
        phone=test_phone
    )

    # assert
    v2_get_users_by_phone_mock.assert_has_calls([
        mocker.call(
            V2GetUsersByPhone(phone=test_phone)
        )
    ])

    assert result == [
        ClientAccountInfo(
            cian_user_id=5,
            email='test5@cian.ru',
            is_agent=True
        ),
        ClientAccountInfo(
            cian_user_id=7,
            email='test7@cian.ru',
            is_agent=False
        )
    ]
