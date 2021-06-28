async def test_send_offers_for_call_called__non_synced_offers_for_call_exist__is_synced_with_kafka(
    pg,
    kafka_service,
    runtime_settings,
    runner,
    offers_and_clients_fixture,
):
    await pg.execute_scripts(offers_and_clients_fixture)

    sql = """
    SELECT COUNT(*) FROM offers_for_call WHERE status IN ('waiting', 'inProgress', 'callMissed', 'callLater');
    """
    expected_count = await pg.fetchval(sql)
    await runtime_settings.set({
        'OFFERS_FOR_CALL_FOR_KAFKA_FETCH_LIMIT': 10,
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-offers-for-call-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=2.5,
        count=expected_count
    )

    # SELECT synced_with_kafka, status FROM offers_for_call;
    sql = """
    SELECT synced_with_kafka, status FROM offers_for_call
    WHERE status NOT IN ('waiting', 'inProgress', 'callMissed', 'callLater');
    """
    non_final_statuses = [
        'waiting',
        'inProgress',
        'callMissed',
        'callLater',
    ]
    rows = await pg.fetch(sql)
    for row in rows:
        if row['status'] not in non_final_statuses:
            assert row['synced_with_kafka'] is True
        else:
            assert row['synced_with_kafka'] is False


async def test_send_offers_for_call_called__final_offers_for_call_exist__correct_messages_count_in_topic(
    pg,
    kafka_service,
    runtime_settings,
    runner,
    offers_and_clients_fixture,
):
    await pg.execute_scripts(offers_and_clients_fixture)

    sql = """
    SELECT COUNT(*) FROM offers_for_call WHERE status NOT IN ('waiting', 'inProgress', 'callMissed', 'callLater');
    """
    expected_count = await pg.fetchval(sql)
    await runtime_settings.set({
        'OFFERS_FOR_CALL_FOR_KAFKA_FETCH_LIMIT': 10,
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-offers-for-call-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='offers-for-call.change',
        timeout=2.5,
        count=expected_count
    )
