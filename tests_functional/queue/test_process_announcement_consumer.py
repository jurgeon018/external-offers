# import asyncio
# from datetime import datetime

# from cian_functional_test_utils.data_fixtures import load_json_data


# async def test_process_announcement_consumer__row_version_is_not_correct__status_is_not_changed(
#     queue_service,
#     pg,
# ):
#     """
#     У обьявления не поменялся статус, изза того что
#     row_version в обьекте из очереди <= row_version обьекта в админке.
#     """
#     # arrange
#     offer = load_json_data(__file__, 'announcement_deactivated.json')
#     row_version = 1 + offer['model']['rowVersion']
#     publication_status = 'Draft'
#     offer_cian_id = offer['model']['id']
#     await pg.execute(f"""
#         INSERT INTO offers_for_call (
#             id, offer_cian_id, publication_status, row_version, parsed_id, client_id, status, created_at, synced_at
#         ) VALUES (
#             1, '{offer_cian_id}', '{publication_status}', {row_version}, '1', '1', 'declined', 'now()', 'now()'
#         )
#     """)
#     # act
#     await queue_service.wait_consumer('external-offers.process_announcement_v2')
#     await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
#     await asyncio.sleep(1)

#     # assert
#     offer_for_call = await pg.fetchrow('SELECT * FROM offers_for_call LIMIT 1')
#     assert offer_for_call['publication_status'] != offer['model']['status']
#     assert offer_for_call['publication_status'] == publication_status
#     assert offer_for_call['row_version'] != offer['model']['rowVersion']
#     assert offer_for_call['row_version'] == row_version


# async def test_process_announcement_consumer__status_is_deactivated__status_is_changed(
#     queue_service,
#     pg,
# ):
#     # arrange
#     offer = load_json_data(__file__, 'announcement_deactivated.json')
#     row_version = 0
#     publication_status = None
#     offer_cian_id = offer['model']['id']
#     await pg.execute("""
#         INSERT INTO clients (
#             client_id, unactivated, calls_count, next_call, status, avito_user_id, client_phones
#         ) VALUES ($1, $2, $3, $4, $5, $6, $7)
#     """, ['1', False, 10, datetime.now(), 'callMissed', '1', ['+789324432000']])
#     await pg.execute(f"""
#         INSERT INTO offers_for_call (
#             id, offer_cian_id, publication_status, row_version, parsed_id, client_id, status, created_at, synced_at
#         ) VALUES (
#             1, '{offer_cian_id}', NULL, {row_version}, '1', '1', 'callMissed', 'now()', 'now()'
#         )
#     """)
#     offer_for_call_before = await pg.fetchrow("""
#         SELECT * FROM offers_for_call LIMIT 1;
#     """)
#     client_before = await pg.fetchrow("""
#         SELECT * FROM clients LIMIT 1;
#     """)
#     # act
#     await queue_service.wait_consumer('external-offers.process_announcement_v2')
#     await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
#     await asyncio.sleep(1)

#     # assert
#     offer_for_call_after = await pg.fetchrow("""
#         SELECT * FROM offers_for_call LIMIT 1;
#     """)
#     client_after = await pg.fetchrow("""
#         SELECT * FROM clients LIMIT 1;
#     """)

#     # set_offer_publication_status_by_offer_cian_id отработала
#     assert offer_for_call_after['publication_status'] != publication_status
#     assert offer_for_call_after['publication_status'] == offer['model']['status']
#     assert offer_for_call_after['row_version'] != row_version
#     assert offer_for_call_after['row_version'] == offer['model']['rowVersion']

#     # set_client_unactivated_by_offer_cian_id, set_client_done_by_offer_cian_id
#     # и set_offer_done_by_offer_cian_id не отработали
#     assert client_after['unactivated'] == client_before['unactivated']
#     assert client_after['calls_count'] == client_before['calls_count']
#     assert client_after['calls_count'] != 0
#     assert client_after['next_call'] == client_before['next_call']
#     assert client_after['status'] == client_before['status']
#     assert client_after['status'] != 'accepted'
#     assert offer_for_call_after['status'] == offer_for_call_before['status']
#     assert offer_for_call_after['status'] != 'done'


# async def test_process_announcement_consumer__status_is_draft__status_is_changed(
#     queue_service,
#     pg,
# ):
#     offer = load_json_data(__file__, 'announcement_draft.json')
#     # arrange
#     row_version = 0
#     publication_status = None
#     offer_cian_id = offer['model']['id']
#     await pg.execute("""
#         INSERT INTO clients (
#             client_id, unactivated, calls_count, next_call, status, avito_user_id, client_phones
#         ) VALUES ($1, $2, $3, $4, $5, $6, $7)
#     """, ['1', False, 10, datetime.now(), 'callMissed', '1', ['+789324432000']])
#     await pg.execute(f"""
#         INSERT INTO offers_for_call (
#             id, offer_cian_id, publication_status, row_version, parsed_id, client_id, status, created_at, synced_at
#         ) VALUES (
#             1, '{offer_cian_id}', NULL, {row_version}, '1', '1', 'callMissed', 'now()', 'now()'
#         )
#     """)
#     offer_for_call_before = await pg.fetchrow("""
#         SELECT * FROM offers_for_call LIMIT 1;
#     """)
#     client_before = await pg.fetchrow("""
#         SELECT * FROM clients LIMIT 1;
#     """)
#     # act
#     await queue_service.wait_consumer('external-offers.process_announcement_v2')
#     await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
#     await asyncio.sleep(1)

#     # assert
#     offer_for_call_after = await pg.fetchrow("""
#         SELECT * FROM offers_for_call LIMIT 1;
#     """)
#     client_after = await pg.fetchrow("""
#         SELECT * FROM clients LIMIT 1;
#     """)

#     # set_offer_publication_status_by_offer_cian_id отработала
#     assert offer_for_call_after['publication_status'] != publication_status
#     assert offer_for_call_after['publication_status'] == offer['model']['status']
#     assert offer_for_call_after['row_version'] != row_version
#     assert offer_for_call_after['row_version'] == offer['model']['rowVersion']

#     # set_client_unactivated_by_offer_cian_id отработала
#     assert client_after['unactivated'] != client_before['unactivated']
#     assert client_after['calls_count'] != client_before['calls_count']
#     assert client_after['calls_count'] == 0
#     assert client_after['next_call'] != client_before['next_call']

#     # set_client_done_by_offer_cian_id и set_offer_done_by_offer_cian_id не отработали
#     assert client_after['status'] == client_before['status']
#     assert client_after['status'] != 'accepted'
#     assert offer_for_call_after['status'] == offer_for_call_before['status']
#     assert offer_for_call_after['status'] != 'done'


# async def test_process_announcement_consumer__status_is_published__status_is_changed(
#     queue_service,
#     pg,
# ):
#     # arrange
#     offer = load_json_data(__file__, 'announcement_published.json')
#     row_version = 0
#     publication_status = None
#     offer_cian_id = offer['model']['id']
#     await pg.execute("""
#         INSERT INTO clients (
#             client_id, unactivated, calls_count, next_call, status, avito_user_id, client_phones
#         ) VALUES ($1, $2, $3, $4, $5, $6, $7)
#     """, ['1', False, 10, datetime.now(), 'callMissed', '1', ['+789324432000']])
#     await pg.execute(f"""
#         INSERT INTO offers_for_call (
#             id, offer_cian_id, publication_status, row_version, parsed_id, client_id, status, created_at, synced_at
#         ) VALUES (
#             1, '{offer_cian_id}', NULL, {row_version}, '1', '1', 'callMissed', 'now()', 'now()'
#         )
#     """)
#     offer_for_call_before = await pg.fetchrow("""
#         SELECT * FROM offers_for_call LIMIT 1;
#     """)
#     client_before = await pg.fetchrow("""
#         SELECT * FROM clients LIMIT 1;
#     """)
#     # act
#     await queue_service.wait_consumer('external-offers.process_announcement_v2')
#     await queue_service.publish('announcement_reporting.change', offer, exchange='announcements')
#     await asyncio.sleep(1)

#     # assert
#     offer_for_call_after = await pg.fetchrow("""
#         SELECT * FROM offers_for_call LIMIT 1;
#     """)
#     client_after = await pg.fetchrow("""
#         SELECT * FROM clients LIMIT 1;
#     """)

#     # set_offer_publication_status_by_offer_cian_id отработала
#     assert offer_for_call_after['publication_status'] != publication_status
#     assert offer_for_call_after['publication_status'] == offer['model']['status']
#     assert offer_for_call_after['row_version'] != row_version
#     assert offer_for_call_after['row_version'] == offer['model']['rowVersion']

#     # set_client_unactivated_by_offer_cian_id не отработала
#     assert client_after['unactivated'] is False
#     assert client_after['calls_count'] == client_before['calls_count']
#     assert client_after['calls_count'] != 0
#     assert client_after['next_call'] is None

#     # set_client_done_by_offer_cian_id и set_offer_done_by_offer_cian_id отработали
#     assert client_after['status'] != client_before['status']
#     assert client_after['status'] == 'accepted'
#     assert offer_for_call_after['status'] != offer_for_call_before['status']
#     assert offer_for_call_after['status'] == 'done'
