import asyncio

import pytest
from cian_functional_test_utils.data_fixtures import load_json_data


@pytest.mark.parametrize('offer', [
    load_json_data(__file__, 'announcement.json')
])
async def test_process_announcement_consumer__row_version_is_correct__status_is_changed(
    runner,
    queue_service,
    pg,
    offer,
):
    """
    У обьявления обновился статус и row_version
    """
    # arrange
    row_version = 0
    publication_status = None
    offer_cian_id = offer['model']['id']
    await pg.execute(f"""
        INSERT INTO offers_for_call (
            id, offer_cian_id, publication_status, row_version, parsed_id, client_id, status, created_at, synced_at
        ) VALUES (
            1, '{offer_cian_id}', NULL, {row_version}, '1', '1', 'declined', 'now()', 'now()'
        )
    """)
    # act
    await runner.start_background_python_command('process_announcement_consumer')
    await queue_service.wait_consumer('external-offers.process_announcement_v2')
    await asyncio.sleep(1)
    await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
    await asyncio.sleep(1)

    # assert
    offer_for_call = await pg.fetchrow('SELECT * FROM offers_for_call LIMIT 1')
    assert offer_for_call['publication_status'] == offer['model']['status']
    assert offer_for_call['row_version'] == offer['model']['rowVersion']
    assert offer_for_call['publication_status'] != publication_status
    assert offer_for_call['row_version'] != row_version


@pytest.mark.parametrize('offer', [
    load_json_data(__file__, 'announcement.json')
])
async def test_process_announcement_consumer__row_version_is_not_correct__status_is_not_changed(
    runner,
    queue_service,
    pg,
    offer,
):
    """
    У обьявления не поменялся статус, изза того что
    row_version в обьекте из очереди <= row_version обьекта в админке.
    """
    # arrange
    row_version = 1 + offer['model']['rowVersion']
    publication_status = 'Draft'
    offer_cian_id = offer['model']['id']
    await pg.execute(f"""
        INSERT INTO offers_for_call (
            id, offer_cian_id, publication_status, row_version, parsed_id, client_id, status, created_at, synced_at
        ) VALUES (
            1, '{offer_cian_id}', '{publication_status}', {row_version}, '1', '1', 'declined', 'now()', 'now()'
        )
    """)
    # act
    await runner.start_background_python_command('process_announcement_consumer')
    await queue_service.wait_consumer('external-offers.process_announcement_v2')
    await asyncio.sleep(1)
    await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
    await asyncio.sleep(1)

    # assert
    offer_for_call = await pg.fetchrow('SELECT * FROM offers_for_call LIMIT 1')
    assert offer_for_call['publication_status'] != offer['model']['status']
    assert offer_for_call['publication_status'] == publication_status
    assert offer_for_call['row_version'] != offer['model']['rowVersion']
    assert offer_for_call['row_version'] == row_version


@pytest.mark.parametrize('offer', [
    load_json_data(__file__, 'simple_announcement_draft.json')
])
async def test_process_announcement_consumer(
    runner,
    queue_service,
    pg,
    offer,
):
    """
    """
    # arrange
    row_version = 1 + offer['model']['rowVersion']
    publication_status = 'Draft'
    offer_cian_id = offer['model']['id']
    await pg.execute(f"""
        INSERT INTO offers_for_call (
            id, offer_cian_id, publication_status, row_version, parsed_id, client_id, status, created_at, synced_at
        ) VALUES (
            1, '{offer_cian_id}', '{publication_status}', {row_version}, '1', '1', 'declined', 'now()', 'now()'
        )
    """)
    # act
    await runner.start_background_python_command('process_announcement_consumer')
    await queue_service.wait_consumer('external-offers.process_announcement_v2')
    await asyncio.sleep(1)
    await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
    await asyncio.sleep(1)

    # assert
    offer_for_call = await pg.fetchrow('SELECT * FROM offers_for_call LIMIT 1')
    # assert offer_for_call['publication_status'] != offer['model']['status']
    # assert offer_for_call['publication_status'] == publication_status
    # assert offer_for_call['row_version'] != offer['model']['rowVersion']
    # assert offer_for_call['row_version'] == row_version
