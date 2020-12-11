import asyncio


async def test_external_offer_callback__new_external_offer__saved(pg, kafka_service, runner):
    # arrange
    offer_data = {
        'phones': ['87771114422'],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'address': 'адресф'
    }
    data = {
        'id': '3c0c865f-3012-4d02-8560-5c644d2c95ba',
        'sourceObjectId': '1_1986816313',
        'sourceUserId': '27d1a87eb7a7cda52167530e424ca317',
        'userSegment': 'c',
        'isCalltracking': False,
        'sourceObjectModel': offer_data,
        'timestamp': '2020-10-26 13:55:00'
    }
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=data
    )

    # act
    await runner.start_background_python_command('save-parsed-offers')
    await asyncio.sleep(5)

    # assert
    row = await pg.fetchrow('SELECT * FROM parsed_offers LIMIT 1')

    row.pop('timestamp')
    row.pop('created_at')
    row.pop('updated_at')
    assert row == {
        'id': '3c0c865f-3012-4d02-8560-5c644d2c95ba',
        'user_segment': 'c',
        'source_object_id': '1_1986816313',
        'source_user_id': '27d1a87eb7a7cda52167530e424ca317',
        'source_object_model': (
            '{"title": "название", "phones": ["87771114422"], '
            '"region": 4628, "address": "адресф", "category": "flatSale", '
            '"description": "описание"}'
        ),
        'is_calltracking': False,
        'synced': False,
    }


async def test_external_offer_callback__existing_external_offer__updated_without_id(pg, kafka_service, runner):
    # arrange
    old_offer_data = {
        'phones': ['87771114422'],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'address': 'адресф'
    }
    old_data = {
        'id': '3c0c865f-3012-4d02-8560-5c644d2c95ba',
        'sourceObjectId': '1_1986816313',
        'sourceUserId': '27d1a87eb7a7cda52167530e424ca317',
        'userSegment': 'c',
        'isCalltracking': False,
        'sourceObjectModel': old_offer_data,
        'timestamp': '2020-10-26 13:55:00'
    }
    new_offer_data = {
        'phones': ['87771114422'],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название новое',
        'description': 'описание новое',
        'address': 'адрес новый'
    }
    new_data = {
        'id': '4c0c865f-3012-4d02-8560-5c644d2c95ba',
        'sourceObjectId': '1_1986816313',
        'sourceUserId': '27d1a87eb7a7cda52167530e424ca317',
        'userSegment': 'c',
        'isCalltracking': False,
        'sourceObjectModel': new_offer_data,
        'timestamp': '2020-10-26 13:55:00'
    }
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=old_data
    )
    await asyncio.sleep(2)
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=new_data
    )
    await asyncio.sleep(2)

    # act
    await runner.start_background_python_command('save-parsed-offers')
    await asyncio.sleep(5)

    # assert
    row = await pg.fetchrow('SELECT * FROM parsed_offers LIMIT 1')

    row.pop('timestamp')
    row.pop('created_at')
    row.pop('updated_at')
    assert row == {
        'id': '3c0c865f-3012-4d02-8560-5c644d2c95ba',
        'user_segment': 'c',
        'source_object_id': '1_1986816313',
        'source_user_id': '27d1a87eb7a7cda52167530e424ca317',
        'source_object_model': (
            '{"title": "название новое", "phones": ["87771114422"], '
            '"region": 4628, "address": "адрес новый", "category": "flatSale", '
            '"description": "описание новое"}'
        ),
        'is_calltracking': False,
        'synced': False,
    }
