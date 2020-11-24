# import asyncio


# async def test_external_offer_callback(pg, kafka_service, runner):
#     # arrange
#     offer_data = {
#         'phones': ['87771114422'],
#         'category': 'flatSale',
#         'region': 4628,
#         'title': 'название',
#         'description': 'описание',
#         'address': 'адресф'
#     }
#     data = {
#         'id': '3c0c865f-3012-4d02-8560-5c644d2c95ba',
#         'sourceObjectId': '1_1986816313',
#         'sourceUserId': '27d1a87eb7a7cda52167530e424ca317',
#         'userSegment': 'c',
#         'isCalltracking': False,
#         'sourceObjectModel': offer_data,
#         'timestamp': '2020-10-26 13:55:00'
#     }
#     await kafka_service.publish(
#         topic='ml-content-copying.change',
#         message=data
#     )

#     # act
#     await runner.start_background_python_command('save-parsed-offers')
#     await asyncio.sleep(5)

#     # assert
#     row = await pg.fetchrow('SELECT * FROM parsed_offers LIMIT 1')

#     row.pop('timestamp')
#     row.pop('created_at')
#     row.pop('updated_at')
#     assert row == {
#         'id': '3c0c865f-3012-4d02-8560-5c644d2c95ba',
#         'user_segment': 'c',
#         'source_object_id': '1_1986816313',
#         'source_user_id': '27d1a87eb7a7cda52167530e424ca317',
#         'source_object_model': (
#             '{"title": "название", "phones": ["87771114422"], '
#             '"region": 4628, "address": "адресф", "category": "flatSale", '
#             '"description": "описание"}'
#         ),
#         'is_calltracking': False,
#         'synced': False,
#         'user_synced': False
#     }
