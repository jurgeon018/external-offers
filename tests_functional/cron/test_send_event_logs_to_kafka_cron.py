async def test_send_offers_for_call_called__final_offers_for_call_exist__correct_messages_count_in_topic(
    pg,
    kafka_service,
    runtime_settings,
    runner,
):
    await pg.execute("""
    INSERT INTO event_log (
        id, offer_id, operator_user_id, status, created_at, call_id
    ) VALUES
    ('1', '1', '1', 'waiting', 'now()', 'call_id'),
    ('2', '2', '2', 'waiting', 'now()', 'call_id');
    """)

    expected_count = await pg.fetchval("""
    SELECT COUNT(*) FROM event_log
    """)
    await runtime_settings.set({
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-event-logs-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='event-logs.change',
        timeout=2.5,
        count=expected_count
    )
