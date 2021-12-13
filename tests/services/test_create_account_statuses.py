import pytest
from cian_test_utils import future

from external_offers.entities.client_account_statuses import (
    ClientAccountStatus,
    HomeownerAccount,
    HomeownerAccountStatus,
)
from external_offers.entities.clients import Client
from external_offers.entities.parsed_offers import ParsedOfferForAccountPrioritization
from external_offers.entities.teams import Team
from external_offers.repositories.monolith_cian_profileapi.entities.get_sanctions_response import (
    GetSanctionsResponse,
    UserSanctions,
)
from external_offers.services.offers_creator import create_client_account_statuses, get_team_info
from external_offers.services.prioritizers.prioritize_homeowner import (
    GetUsersByPhoneResponseV2,
    UserModelV2,
    find_homeowner_account,
    find_homeowner_client_account_priority,
)
from external_offers.services.prioritizers.prioritize_smb import find_smb_client_account_priority


async def test_create_client_account_statuses(mocker):
    # arrange
    mocker.patch(
        'external_offers.services.offers_creator.runtime_settings',
        new={
            'ENABLE_CLIENT_ACCOUNT_STATUSES_CASHING': False,
        }
    )
    get_parsed_offers_for_account_prioritization_mock = mocker.patch(
        'external_offers.services.offers_creator.get_parsed_offers_for_account_prioritization',
    )

    # act
    await create_client_account_statuses()

    # assert
    assert get_parsed_offers_for_account_prioritization_mock.assert_not_called


async def test_find_smb_client_account_priority__invalid_account_status(
    mocker,
):
    # arrange
    invalid_account_status = 'str'
    mocker.patch(
        'external_offers.services.prioritizers.prioritize_smb.find_smb_client_account_status_by_announcements_count',
        return_value=future(invalid_account_status),
    )
    # act
    with pytest.raises(Exception) as err:
        await find_smb_client_account_priority(
            client_count=10,
            client=mocker.MagicMock(value=[]),
            team_settings={},
            client_account_statuses=None,
        )
    # assert
    assert str(err.value) == f'Unhandled account status: {invalid_account_status}, <class \'str\'>'


async def test_find_homeowner_client_account_priority__invalid_account_status(
    mocker,
):
    # arrange
    invalid_account_status = 'str'
    # act
    with pytest.raises(Exception) as err:
        await find_homeowner_client_account_priority(
            client=Client(
                cian_user_id=None,
                client_id='123456',
                avito_user_id='12345',
                client_phones=['+7800234243'],
                status='waiting',
            ),
            team_settings={},
            client_account_statuses={
                '+7800234243': ClientAccountStatus(
                    homeowner_account_status=invalid_account_status,
                    new_cian_user_id=None,
                )
            },
        )
    # assert
    assert str(err.value) == f'Unhandled account status: {invalid_account_status}, <class \'str\'>'


async def test_get_team_info(mocker):
    # arrange
    mocker.patch(
        'external_offers.services.offers_creator.runtime_settings',
        new={
            'MAIN_REGIONS_PRIORITY': {'1': 1, '2': 2},
        }
    )
    # act
    team_id, team_settings = get_team_info(Team(
        team_id=1,
        lead_id=1,
        team_name='team 1',
        settings='{}'
    ))
    # assert
    assert team_id == 1
    assert team_settings['main_regions_priority'] == {'1': 1, '2': 2}


async def test_create_client_account_statuses__phones_are_cashed_phonens(
    mocker,
):
    # arrange
    find_smb_account_mock = mocker.patch(
        'external_offers.services.offers_creator.find_smb_account',
    )
    find_homeowner_account_mock = mocker.patch(
        'external_offers.services.offers_creator.find_homeowner_account',
    )
    set_client_account_status_mock = mocker.patch(
        'external_offers.services.offers_creator.set_client_account_status',
    )
    mocker.patch(
        'external_offers.services.offers_creator.get_parsed_offers_for_account_prioritization',
        return_value=future([
            ParsedOfferForAccountPrioritization(
                phones='["+780834434"]',
                user_segment='c',
            ),
            ParsedOfferForAccountPrioritization(
                phones='["880834431"]',
                user_segment='d',
            ),
        ])
    )
    mocker.patch(
        'external_offers.services.offers_creator.get_recently_cashed_client_account_statuses',
        return_value=future([
            '+780834434',
            '+780834431',
        ])
    )
    # act
    await create_client_account_statuses()
    # assert
    find_smb_account_mock.assert_not_called()
    find_homeowner_account_mock.assert_not_called()
    set_client_account_status_mock.assert_not_called()


async def test_find_homeowner_client_account_priority__client_has_cian_user_id():
    cian_user_id = 1234
    active_lk_homeowner_priority = 100
    # act
    result = await find_homeowner_client_account_priority(
        client=Client(
            cian_user_id=cian_user_id,
            client_id='123456',
            avito_user_id='12345',
            client_phones=['+7800234243'],
            status='waiting',
        ),
        team_settings={'active_lk_homeowner_priority': active_lk_homeowner_priority}
    )
    # assert
    assert result == active_lk_homeowner_priority


async def test_find_homeowner_account(mocker):
    # arrange
    mocker.patch(
        'external_offers.services.prioritizers.prioritize_homeowner.runtime_settings',
        new={
            'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        }
    )
    mocker.patch(
        'external_offers.services.prioritizers.prioritize_homeowner.v2_get_users_by_phone',
        return_value=future(GetUsersByPhoneResponseV2(
            users=[UserModelV2(id=12345)]
        ))
    )
    mocker.patch(
        'external_offers.services.prioritizers.prioritize_homeowner.v1_sanctions_get_sanctions',
        return_value=future(GetSanctionsResponse(
            items=[UserSanctions(user_id=12345, sanctions=[])]
        ))
    )
    phone = '+783434332'
    # act
    result = await find_homeowner_account(phone)
    # assert
    assert result == HomeownerAccount(
        new_cian_user_id=None,
        account_status=HomeownerAccountStatus.has_sanctions,
    )
