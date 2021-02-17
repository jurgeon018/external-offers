async def test_send_offers_for_call_called__offers_for_call_exist__correct_messages_count_in_topic(
    pg,
    kafka_service,
    runtime_settings,
    runner,
    offers_and_clients_fixture,
):
    await pg.execute_scripts(offers_and_clients_fixture)

    expected_count = await pg.fetchval('SELECT COUNT(*) FROM offers_for_call;')
    await runtime_settings.set({
        'OFFERS_FOR_CALL_FOR_KAFKA_FETCH_LIMIT': 10,
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-offers-for-call-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=1.5,
        count=expected_count
    )
