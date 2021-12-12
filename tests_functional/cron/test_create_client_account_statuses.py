from unittest.mock import ANY

import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse


async def v2_get_users_by_phone_add_stub(
    users: list,
    phone: str,
    users_mock,
) -> None:
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        query={
            'phone': phone,
        },
        response=MockResponse(body={'users': users}),
    )


async def v1_sanctions_get_sanctions_add_stub(
    items: list,
    user_ids: list,
    monolith_cian_profileapi_mock,
) -> None:
    await monolith_cian_profileapi_mock.add_stub(
        method='GET',
        path='/v1/sanctions/get-sanctions/',
        query={
            'user_ids': user_ids,
            # 'userIds': user_ids,
        },
        response=MockResponse(body={'items': items}),
    )


@pytest.mark.parametrize('use_client_account_statuses', [
    True,
    False,
])
async def test_create_client_account_statuses__statuses_are_created(
    pg,
    runtime_settings,
    runner,
    monolith_cian_profileapi_mock,
    users_mock,
    logs,
    parsed_offers_and_numbers_for_account_prioritization_fixture,
    use_client_account_statuses,
):
    # arrange
    await runtime_settings.set({
        # настройки для кеширования статусов аккаунтов
        'CLIENT_ACCOUNT_STATUSES_UPDATE_CHECK_WINDOW_IN_DAYS': 5,
        'ENABLE_CLIENT_ACCOUNT_STATUSES_CASHING': True,
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        # настройки для приоретизации
        'OFFER_TASK_CREATION_REGIONS': [4150],
        'OFFER_TASK_CREATION_SEGMENTS': ['c', 'd'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale'],
    })
    await pg.execute_scripts(parsed_offers_and_numbers_for_account_prioritization_fixture)
    await monolith_cian_profileapi_mock.add_stub(
        method='GET', path='/v1/sanctions/get-sanctions/', response=MockResponse(body={'items': []})
    )

    account_1_c_phone = '+70000001'
    account_1_c_inner_phone = '80000001'
    expected_offer_1_c = {
        'priority': 231200111
    }
    expected_account_1_c = {
        'smb_account_status': 'no_lk_smb_priority',  # not user_profiles
        'phone': account_1_c_phone,
        'new_cian_user_id': None,
        'homeowner_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
    }

    await v2_get_users_by_phone_add_stub([], account_1_c_phone, users_mock)

    # account_2_c_phone = '+70000002'
    # account_2_c_cian_user_id = 2
    # expected_account_2_c = {
    #     'smb_account_status': 'has_sanctions',
    #     'phone': account_2_c_phone,
    #     'new_cian_user_id': None,
    #     'homeowner_account_status': None, 'created_at': ANY, 'updated_at': ANY,
    # }
    # await v2_get_users_by_phone_add_stub([{
    #     'id': account_2_c_cian_user_id,
    #     'cianUserId': account_2_c_cian_user_id,
    #     'state': 'active',
    # }], account_2_c_phone, users_mock)
    # await v1_sanctions_get_sanctions_add_stub([{
    #     'userId': account_2_c_cian_user_id,
    #     'sanctions': [{
    #         'sanctionId': 9072881,
    #         'sanctionName': 'Запрет на публикацию объявлений',
    #         'sanctionEnd': None
    #     }]  # -> has_sanctions
    # }], [account_2_c_cian_user_id], monolith_cian_profileapi_mock)

    account_3_c_phone = '+70000003'
    account_3_c_inner_phone = '80000003'
    account_3_c_cian_user_id = 3
    expected_offer_3_c = {
        'priority': -1
    }
    expected_account_3_c = {
        'smb_account_status': 'has_bad_account',
        'phone': account_3_c_phone,
        'new_cian_user_id': None,
        'homeowner_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
    }
    await v2_get_users_by_phone_add_stub(
        [
            {
                'id': account_3_c_cian_user_id,
                'cianUserId': account_3_c_cian_user_id,
                'state': 'blocked',  # -> has_bad_account
            }
        ],
        account_3_c_phone,
        users_mock,
    )

    account_4_c_phone = '+70000004'
    account_4_c_inner_phone = '80000004'
    account_4_c_cian_user_id = 4
    expected_offer_4_c = {
        'priority': -1
    }
    expected_account_4_c = {
        'smb_account_status': 'has_wrong_user_source_type',
        'phone': account_4_c_phone,
        'new_cian_user_id': None,
        'homeowner_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
    }
    await v2_get_users_by_phone_add_stub(
        [
            {
                'id': account_4_c_cian_user_id,
                'cianUserId': account_4_c_cian_user_id,
                'state': 'active',
                'externalUserSourceType': 'subAgents',  # -> has_wrong_user_source_type
            }
        ],
        account_4_c_phone,
        users_mock,
    )

    account_5_c_phone = '+70000005'
    account_5_c_inner_phone = '80000005'
    account_5_c_cian_user_id = 5
    expected_offer_5_c = {
        'priority': 231200111
    }
    expected_account_5_c = {
        'smb_account_status': 'no_lk_smb_priority',  # not result.chosen_profile
        'phone': account_5_c_phone,
        'new_cian_user_id': None,
        'homeowner_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
    }
    await v2_get_users_by_phone_add_stub(
        [
            {
                'id': account_5_c_cian_user_id,
                'cianUserId': account_5_c_cian_user_id,
                'state': 'active',
                'externalUserSourceType': None,
                'isAgent': False,  # -> no_lk_smb_priority
            }
        ],
        account_5_c_phone,
        users_mock,
    )

    account_6_c_phone = '+70000006'
    account_6_c_inner_phone = '80000006'

    expected_offer_6_c = {
        'priority': -1
    }
    expected_account_6_c = {
        'smb_account_status': 'api_client_exception',
        'phone': account_6_c_phone,
        'new_cian_user_id': None,
        'homeowner_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
    }

    account_7_c_phone = '+70000007'
    account_7_c_inner_phone = '80000007'
    account_7_c_cian_user_id = 7
    expected_offer_7_c = {
        'priority': -1
    }
    expected_account_7_c = {
        'smb_account_status': None,
        'phone': account_7_c_phone,
        'new_cian_user_id': account_7_c_cian_user_id,
        'homeowner_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
    }
    await v2_get_users_by_phone_add_stub(
        [
            {
                'id': account_7_c_cian_user_id,
                'cianUserId': account_7_c_cian_user_id,
                'state': 'active',
                'externalUserSourceType': None,
                'isAgent': True,
            }
        ],
        account_7_c_phone,
        users_mock,
    )

    account_11_d_phone = '+70000011'
    account_11_d_inner_phone = '80000011'
    account_11_d_cian_user_id = 11
    expected_offer_11_d = {
        'priority': 232200211
    }
    expected_account_11_d = {
        'phone': account_11_d_phone,
        'homeowner_account_status': 'active_lk_homeowner_priority',
        'smb_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
        'new_cian_user_id': account_11_d_cian_user_id,
    }
    await v2_get_users_by_phone_add_stub(
        [
            {
                'id': account_11_d_cian_user_id,
                'cianUserId': account_11_d_cian_user_id,
                'state': 'active',
                'externalUserSourceType': None,
                'isAgent': False,
            }
        ],
        account_11_d_phone,
        users_mock,
    )

    account_12_d_phone = '+70000012'
    account_12_d_inner_phone = '80000012'
    expected_offer_12_d = {
        'priority': 232200111
    }
    expected_account_12_d = {
        'phone': account_12_d_phone,
        'homeowner_account_status': 'no_lk_homeowner_priority',  # not user_profiles
        'smb_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
        'new_cian_user_id': None,
    }
    await v2_get_users_by_phone_add_stub([], account_12_d_phone, users_mock)

    account_13_d_phone = '+70000013'
    account_13_d_inner_phone = '80000013'
    account_13_d_cian_user_id = 13
    expected_offer_13_d = {
        'priority': 232200111
    }
    expected_account_13_d = {
        'phone': account_13_d_phone,
        'homeowner_account_status': 'no_lk_homeowner_priority',  # not result.chosen_profile
        'smb_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
        'new_cian_user_id': None,
    }
    await v2_get_users_by_phone_add_stub(
        [
            {
                'id': account_13_d_cian_user_id,
                'cianUserId': account_13_d_cian_user_id,
                'state': 'active',
                'externalUserSourceType': None,
                'isAgent': True,
            }
        ],
        account_13_d_phone,
        users_mock,
    )

    # account_14_d_phone = '+70000014'
    # account_14_d_cian_user_id = 14
    # expected_account_14_d = {
    #     'phone': account_14_d_phone,
    #     'homeowner_account_status': 'has_existing_accounts',
    #     'smb_account_status': None, 'created_at': ANY, 'updated_at': ANY,
    #     'new_cian_user_id': None,
    # }
    # await v2_get_users_by_phone_add_stub([{
    #     'id': account_14_d_cian_user_id,
    # }], account_14_d_phone, users_mock)

    # account_15_d_phone = '+70000015'
    # account_15_d_cian_user_id = 15
    # expected_account_15_d = {
    #     'phone': account_15_d_phone,
    #     'homeowner_account_status': 'has_sanctions',
    #     'smb_account_status': None, 'created_at': ANY, 'updated_at': ANY,
    #     'new_cian_user_id': None,
    # }
    # await v2_get_users_by_phone_add_stub([{
    #     'id': account_15_d_cian_user_id,
    #     'cianUserId': account_15_d_cian_user_id,
    #     'state': 'active',
    # }], account_15_d_phone, users_mock)
    # await v1_sanctions_get_sanctions_add_stub([{
    #     'userId': account_15_d_cian_user_id,
    #     'sanctions': [{
    #         'sanctionId': 9072881,
    #         'sanctionName': 'Запрет на публикацию объявлений',
    #         'sanctionEnd': None
    #     }]  # -> has_sanctions
    # }], [account_15_d_cian_user_id], monolith_cian_profileapi_mock)

    account_16_d_phone = '+70000016'
    account_16_d_inner_phone = '80000016'
    account_16_c_cian_user_id = 16
    expected_offer_16_d = {
        'priority': -1
    }
    expected_account_16_d = {
        'phone': account_16_d_phone,
        'homeowner_account_status': 'has_bad_account',
        'smb_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
        'new_cian_user_id': None,
    }
    await v2_get_users_by_phone_add_stub(
        [
            {
                'id': account_16_c_cian_user_id,
                'cianUserId': account_16_c_cian_user_id,
                'state': 'blocked',  # -> has_bad_account
            }
        ],
        account_16_d_phone,
        users_mock,
    )

    account_17_d_phone = '+70000017'
    account_17_d_inner_phone = '80000017'
    account_17_c_cian_user_id = 17
    expected_offer_17_d = {
        'priority': -1
    }
    expected_account_17_d = {
        'phone': account_17_d_phone,
        'homeowner_account_status': 'has_wrong_user_source_type',
        'smb_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
        'new_cian_user_id': None,
    }
    await v2_get_users_by_phone_add_stub(
        [
            {
                'id': account_17_c_cian_user_id,
                'cianUserId': account_17_c_cian_user_id,
                'state': 'active',
                'externalUserSourceType': 'subAgents',  # -> has_wrong_user_source_type
            }
        ],
        account_17_d_phone,
        users_mock,
    )

    account_18_d_phone = '+70000018'
    account_18_d_inner_phone = '80000018'
    expected_offer_18_d = {
        'priority': -1
    }
    expected_account_18_d = {
        'phone': account_18_d_phone,
        'homeowner_account_status': 'api_client_exception',
        'smb_account_status': None,
        'created_at': ANY,
        'updated_at': ANY,
        'new_cian_user_id': None,
    }

    # 'c' - smb v2_get_user_active_announcements_count stub

    # act
    if use_client_account_statuses:
        await runner.run_python_command('create-client-account-statuses-cron')
    await runner.run_python_command('create-offers-for-call')

    # assert
    parsed_offers_count = await pg.fetchval(
        """
        SELECT COUNT(*)
        FROM parsed_offers
        WHERE (parsed_offers.source_object_model -> 'phones') != $1
        AND (parsed_offers.source_object_model -> 'phones') != $2
        AND (parsed_offers.source_object_model -> 'phones') != $3
        AND parsed_offers.user_segment IS NOT NULL
        AND parsed_offers.user_segment IN ('c', 'd')
        AND parsed_offers.source_user_id IS NOT NULL
        AND NOT parsed_offers.is_calltracking
    """,
        ['[]', 'null', '[""]'],
    )
    assert parsed_offers_count == 15

    if use_client_account_statuses:
        client_account_statuses = await pg.fetch(
            """
        select * from client_account_statuses
        """
        )
        # 6 - количество записей из фикстуры
        assert len(client_account_statuses) == 6 + parsed_offers_count
        assert any(
            (
                f'Кеширование приоритетов по ЛК для {parsed_offers_count} обьявлений запущено.' in line
                for line in logs.get_lines()
            )
        )
        accounts_query = """
        select *
        from client_account_statuses
        where phone = '%s'
        """

        assert expected_account_1_c == await pg.fetchrow(accounts_query % account_1_c_phone)
        assert expected_account_3_c == await pg.fetchrow(accounts_query % account_3_c_phone)
        assert expected_account_4_c == await pg.fetchrow(accounts_query % account_4_c_phone)
        assert expected_account_5_c == await pg.fetchrow(accounts_query % account_5_c_phone)
        assert expected_account_6_c == await pg.fetchrow(accounts_query % account_6_c_phone)
        assert expected_account_7_c == await pg.fetchrow(accounts_query % account_7_c_phone)

        assert expected_account_11_d == await pg.fetchrow(accounts_query % account_11_d_phone)
        assert expected_account_12_d == await pg.fetchrow(accounts_query % account_12_d_phone)
        assert expected_account_13_d == await pg.fetchrow(accounts_query % account_13_d_phone)
        assert expected_account_16_d == await pg.fetchrow(accounts_query % account_16_d_phone)
        assert expected_account_17_d == await pg.fetchrow(accounts_query % account_17_d_phone)
        assert expected_account_18_d == await pg.fetchrow(accounts_query % account_18_d_phone)

    offers_query = """
    select
        priority
        -- user_segment,
        -- segment,
        -- source_object_model->'phones' as phones,
        -- client_phones,
        -- clients.status as clients_status,
        -- offers_for_call.status as offers_for_call_status,
        -- cian_user_id
    from offers_for_call
    join clients on clients.client_id = offers_for_call.client_id
    join parsed_offers on parsed_offers.id = offers_for_call.parsed_id
    where client_phones[1] = '%s'
    """
    assert expected_offer_1_c == await pg.fetchrow(offers_query % account_1_c_inner_phone)
    assert expected_offer_3_c == await pg.fetchrow(offers_query % account_3_c_inner_phone)
    assert expected_offer_4_c == await pg.fetchrow(offers_query % account_4_c_inner_phone)
    assert expected_offer_5_c == await pg.fetchrow(offers_query % account_5_c_inner_phone)
    assert expected_offer_6_c == await pg.fetchrow(offers_query % account_6_c_inner_phone)
    assert expected_offer_7_c == await pg.fetchrow(offers_query % account_7_c_inner_phone)

    assert expected_offer_11_d == await pg.fetchrow(offers_query % account_11_d_inner_phone)
    assert expected_offer_12_d == await pg.fetchrow(offers_query % account_12_d_inner_phone)
    assert expected_offer_13_d == await pg.fetchrow(offers_query % account_13_d_inner_phone)
    assert expected_offer_16_d == await pg.fetchrow(offers_query % account_16_d_inner_phone)
    assert expected_offer_17_d == await pg.fetchrow(offers_query % account_17_d_inner_phone)
    assert expected_offer_18_d == await pg.fetchrow(offers_query % account_18_d_inner_phone)
