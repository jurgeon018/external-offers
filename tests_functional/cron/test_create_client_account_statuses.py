from cian_functional_test_utils.pytest_plugin import MockResponse


async def v2_get_users_by_phone_add_stub(
    users_mock,
    cian_user_ids: list[str] = None,
    phone: str = None,
) -> None:
    if cian_user_ids is None:
        cian_user_ids = [1000000]
    if phone is None:
        query = None
    else:
        query = {
            'phone': phone,
        }
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        query=query,
        response=MockResponse(
            body={
                'users': [
                    {
                        'id': None,
                        'cianUserId': cian_user_id,
                        'mainAnnouncementsRegionId': None,
                        'email': None,
                        'state': None,
                        'stateChangeReason': None,
                        'secretCode': None,
                        'birthday': None,
                        'firstName': None,
                        'lastName': None,
                        'city': None,
                        'userName': None,
                        'creationDate': None,
                        'ip': None,
                        'externalUserSourceType': None,
                        'isAgent': None,
                    } for cian_user_id in cian_user_ids
                ]
            }
        )
    )


async def test_create_client_account_statuses__statuses_are_created(
    pg,
    runtime_settings,
    runner,
    users_mock,
    logs,
    parsed_offers_and_numbers_for_account_prioritization_fixture,
):
    # arrange
    parsed_offers_count_query, parsed_offers_count_params = """
        SELECT COUNT(*)
        FROM parsed_offers
        WHERE (parsed_offers.source_object_model -> 'phones') != $1
        AND (parsed_offers.source_object_model -> 'phones') != $2
        AND (parsed_offers.source_object_model -> 'phones') != $3
        AND parsed_offers.user_segment IS NOT NULL
        AND parsed_offers.user_segment IN ('c', 'd')
        AND parsed_offers.source_user_id IS NOT NULL
        AND NOT parsed_offers.is_calltracking
    """, [
        '[]',
        'null',
        '[""]',
    ]
    await runtime_settings.set({
        'client_account_statuses_UPDATE_CHECK_WINDOW_IN_DAYS': 5,
        'ENABLE_client_account_statuses_CASHING': True,
    })
    await pg.execute_scripts(parsed_offers_and_numbers_for_account_prioritization_fixture)
    # 'c' - smb
    # parsed_offer1 = await pg.fetchrow('select * from parsed_offers where id=1')
    # parsed_offer2 = await pg.fetchrow('select * from parsed_offers where id=2')
    # parsed_offer3 = await pg.fetchrow('select * from parsed_offers where id=3')
    # parsed_offer4 = await pg.fetchrow('select * from parsed_offers where id=4')
    # 'd' - homeowner
    # parsed_offer12 = await pg.fetchrow('select * from parsed_offers where id=12')
    # parsed_offer13 = await pg.fetchrow('select * from parsed_offers where id=13')
    # parsed_offer14 = await pg.fetchrow('select * from parsed_offers where id=14')

    # TODO: arrange stubs for find_smb_account
    # TODO: v2_get_users_by_phone
    await v2_get_users_by_phone_add_stub(users_mock)
    await v2_get_users_by_phone_add_stub(users_mock, cian_user_ids=[1, 2], phone='12345')
    await v2_get_users_by_phone_add_stub(users_mock, cian_user_ids=[3, 4], phone='54321')
    # TODO: v1_sanctions_get_sanctions
    # TODO: v2_get_user_active_announcements_count

    # TODO: arrange stubs for find_homeowner_account
        # TODO: v2_get_users_by_phone
        # TODO: v1_sanctions_get_sanctions

    # act
    await runner.run_python_command('create-client-account-statuses-cron')

    # assert
    parsed_offers_count = await pg.fetchval(parsed_offers_count_query, parsed_offers_count_params)
    assert any([
        f'Кеширование приоритетов по ЛК для {parsed_offers_count} обьявлений запущено.'
        in line for line in logs.get_lines()
    ])
    assert parsed_offers_count == 7

    # TODO: assert client_account_statuses


# async def test_create_client_account_statuses__statuses_are_used_in_prioritization(
#     pg,
#     kafka_service,
#     runtime_settings,
#     runner,
# ):
#     # arrange


#     # act
#     await runner.run_python_command('create-phones-statuses-cron')
#     await runner.run_python_command('create-offers-for-call-from-parsed')

#     # assert

