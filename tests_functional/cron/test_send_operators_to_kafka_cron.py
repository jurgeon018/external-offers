async def test_send_offers_for_call_called__final_offers_for_call_exist__correct_messages_count_in_topic(
    pg,
    kafka_service,
    runtime_settings,
    runner,
):
    await pg.execute("""
    INSERT INTO operators (
        operator_id, is_teamlead, full_name, team_id, email, created_at, updated_at
    ) VALUES
    ('1', 't', 'оператор 1', '1', 'email1@cian.ru', 'now()', 'now()'),
    ('2', 't', 'оператор 2', '2', 'email2@cian.ru', 'now()', 'now()');
    """)

    expected_count = await pg.fetchval("""
    SELECT COUNT(*) FROM operators
    """)
    await runtime_settings.set({
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-operators-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='operators.change',
        timeout=2.5,
        count=expected_count
    )
