import pytest


@pytest.mark.parametrize(
    'operators_actions',
    [
        # небыло обработано ниодного обьявления, все обьявления в ожидании
        """
        UPDATE clients SET status = 'waiting';
        UPDATE offers_for_call SET status = 'waiting';
        """,

        # была обработана часть обьявлений, часть обьявлений в ожидании
        """
        UPDATE offers_for_call SET status = 'inProgress'
            WHERE status='waiting' AND random() > 0.5;
        UPDATE clients SET status = 'inProgress'
            WHERE status='waiting' AND random() > 0.5;
        """,

        # было обработано все обьявления, нет ниодного обьявления в ожидании
        """
        UPDATE offers_for_call SET status = 'inProgress';
        UPDATE clients SET status = 'inProgress';
        """,
    ]
)
async def test_sync_with_grafana(
    pg,
    runner,
    segmentation_rows_fixture,
    operators_actions,
):
    # arrange
    await pg.execute_scripts(segmentation_rows_fixture)
    synced_offers_sql = """
    SELECT COUNT(*) FROM offers_for_call
    WHERE synced_with_grafana IS TRUE;
    """
    synced_clients_sql = """
    SELECT COUNT(*) FROM clients
    WHERE synced_with_grafana IS TRUE;
    """
    expected_synced_offers_after_sync_sql = """
    SELECT COUNT(*) FROM offers_for_call
    WHERE synced_with_grafana IS NOT TRUE
    AND status = 'waiting'
    AND client_id IN (
        SELECT client_id
        FROM offers_for_call
        GROUP BY client_id
        HAVING count(1) > 1
    );
    """
    expected_synced_clients_after_sync_sql = """
    SELECT COUNT(*) FROM clients
    WHERE synced_with_grafana IS NOT TRUE
    AND status = 'waiting'
    AND client_id IN (
        SELECT client_id
        FROM offers_for_call
        GROUP BY client_id
        HAVING count(1) > 1
    );
    """
    expected_synced_offers_after_sync = await pg.fetchval(expected_synced_offers_after_sync_sql)
    expected_synced_clients_after_sync = await pg.fetchval(expected_synced_clients_after_sync_sql)
    synced_offers_before_sync = await pg.fetchval(synced_offers_sql)
    synced_clients_before_sync = await pg.fetchval(synced_clients_sql)

    # act
    # утренний крон
    await runner.run_python_command('send-waiting-offers-and-clients-amount-to-grafana-cron')

    # имитация действий операторов в течении рабочего дня
    await pg.execute(operators_actions)

    synced_offers_after_sync = await pg.fetchval(synced_offers_sql)
    synced_clients_after_sync = await pg.fetchval(synced_clients_sql)

    # вечерний крон
    await runner.run_python_command('send-processed-offers-and-clients-amount-to-grafana-cron')

    synced_offers_after_unsync = await pg.fetchval(synced_offers_sql)
    synced_clients_after_unsync = await pg.fetchval(synced_clients_sql)

    # assert
    assert synced_offers_before_sync == 0
    assert synced_clients_before_sync == 0
    assert synced_offers_after_sync == expected_synced_offers_after_sync
    assert synced_clients_after_sync == expected_synced_clients_after_sync
    assert synced_offers_after_unsync == 0
    assert synced_clients_after_unsync == 0
