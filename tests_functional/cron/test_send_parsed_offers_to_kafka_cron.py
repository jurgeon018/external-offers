async def test_send_parsed_offers_called__parsed_offers_exist__correct_messages_count_in_topic(
    pg,
    kafka_service,
    runtime_settings,
    runner,
    parsed_offers_fixture,
):
    await pg.execute_scripts(parsed_offers_fixture)

    expected_count = await pg.fetchval('SELECT COUNT(*) FROM parsed_offers;')
    await runtime_settings.set({
        'PARSED_OFFERS_FOR_KAFKA_FETCH_LIMIT': 10,
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-parsed-offers-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='parsed-offer.change',
        timeout=2.5,
        count=expected_count
    )
