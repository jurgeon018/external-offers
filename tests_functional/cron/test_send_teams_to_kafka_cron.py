async def test_send_offers_for_call_called__final_offers_for_call_exist__correct_messages_count_in_topic(
    pg,
    kafka_service,
    runtime_settings,
    runner,
):
    await pg.execute("""
    INSERT INTO teams (team_id, team_name, lead_id) VALUES
    ('1', 'team1', '1'),
    ('2', 'team2', '2');
    """)

    expected_count = await pg.fetchval("""
    SELECT COUNT(*) FROM teams
    """)
    await runtime_settings.set({
        'DEFAULT_KAFKA_TIMEOUT': 2
    })

    await runner.run_python_command('send-teams-to-kafka-cron')

    await kafka_service.wait_messages(
        topic='external-offers-teams.change',
        timeout=2.5,
        count=expected_count
    )
