async def test_send_offers_for_call_called__final_offers_for_call_exist__correct_messages_count_in_topic(
    pg,
    kafka_service,
    runtime_settings,
    runner,
):

    await pg.execute("""
    INSERT INTO clients (
        client_id,avito_user_id,client_phones,status,synced_with_grafana,is_test,main_account_chosen,unactivated
    ) VALUES
    ('1', '1', '{+88005553535}',  'waiting', 'f',  'f',  'f', 'f'),
    ('2', '2', '{+88005553535}',  'waiting', 'f',  'f',  'f', 'f');
    """)

    expected_count = await pg.fetchval("""
    SELECT COUNT(*) FROM clients
    """)
    await runtime_settings.set({
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-clients-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='external-offers-clients.change',
        timeout=2.5,
        count=expected_count
    )