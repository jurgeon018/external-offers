async def test_send_clients_called__non_synced_clients_exist__is_synced_with_kafka(
    pg,
    kafka_service,
    runtime_settings,
    runner,
    offers_and_clients_fixture,
):
    await pg.execute_scripts(offers_and_clients_fixture)

    sql = """
    SELECT COUNT(*) FROM clients WHERE status IN ('waiting', 'inProgress', 'callMissed', 'callLater');
    """
    expected_count = await pg.fetchval(sql)
    await runtime_settings.set({
        'CLIENTS_FOR_KAFKA_FETCH_LIMIT': 10,
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-clients-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='external-offers-clients.change',
        timeout=2.5,
        count=expected_count
    )

    sql = """
    SELECT synced_with_kafka, status FROM clients;
    """
    non_final_statuses = [
        'waiting',
        'inProgress',
        'callMissed',
        'callLater',
    ]
    rows = await pg.fetch(sql)
    for row in rows:
        if row['status'] in non_final_statuses:
            assert not row['synced_with_kafka']
        else:
            assert row['synced_with_kafka']


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
