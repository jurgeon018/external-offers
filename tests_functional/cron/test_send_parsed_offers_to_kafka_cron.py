from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_send_parsed_offers_called__parsed_offers_exist__correct_messages_count_in_topic(
    pg,
    kafka_service,
    runtime_settings,
    runner,
    parsed_offers_fixture,
):
    await pg.execute_scripts(parsed_offers_fixture)

    sql = """
    SELECT COUNT(*) FROM parsed_offers WHERE created_at >= now() - interval '1 days';
    """
    expected_count = await pg.fetchval(sql)
    await runtime_settings.set({
        'PARSED_OFFERS_FOR_KAFKA_FETCH_LIMIT': 10,
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-parsed-offers-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='parsed-offers.change',
        timeout=2.5,
        count=expected_count
    )


async def test_send_parsed_offers__check_external_offer_type_in_offers_for_call__is_commercial(
    pg,
    kafka_service,
    users_mock,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['officeRent', 'officeSale'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE external_offer_type = 'commercial'
        """
    )
    assert row['parsed_id'] == '821ff03a-573c-4bac-8599-28f17e68a0d8'
    assert row['status'] == 'waiting'
    assert row['external_offer_type'] == 'commercial'
