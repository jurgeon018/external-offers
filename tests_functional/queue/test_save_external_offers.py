import asyncio

import pytest
from cian_functional_test_utils import DependencyType
from cian_functional_test_utils.pytest_plugin import KafkaService, Runner
from confluent_kafka.admin import AdminClient
from confluent_kafka.cimpl import NewTopic


async def _create_topic(kafka_service: KafkaService, kafka_addr: str, topic: str) -> None:
    # TODO: https://jira.cian.tech/browse/ML-12130
    client = AdminClient({'bootstrap.servers': kafka_addr})
    client.create_topics([NewTopic(topic=topic, num_partitions=1)])

    while True:
        topics = await kafka_service._producer.list_topics(timeout=1)
        if topic in topics:
            break
        await asyncio.sleep(0.5)


@pytest.fixture(autouse=True)
async def delete_all_topics_before_test(kafka_service):
    # при тестировании консьюмера топики удалять не нужно, переопределяем
    # дефолтную фикстуру
    pass


@pytest.fixture(scope='module', autouse=True)
async def run_consumer(runner: Runner, kafka_service: KafkaService, dependencies):
    host, port = dependencies.get(type_=DependencyType.kafka, alias='default', port=9092)
    await _create_topic(kafka_service, kafka_addr=f'{host}:{port}', topic='ml-content-copying.change')

    await runner.start_background_python_command('save-parsed-offers')


async def test_external_offer_callback__new_external_offer__saved(pg, kafka_service):
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
    await asyncio.sleep(3)
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


async def test_external_offer_callback__existing_external_offer__updated_without_id(pg, kafka_service):
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
    await asyncio.sleep(3)
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=new_data
    )
    await asyncio.sleep(3)

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
