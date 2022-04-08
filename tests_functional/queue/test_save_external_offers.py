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
        topics = kafka_service._admin_client.list_topics()
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


async def test_external_offer_callback__existing_external_offer__updated_without_id(
    pg,
    kafka_service
):
    # arrange
    source_object_id = '1_1986816313'
    parsed_id1 = '3c0c865f-3012-4d02-8560-5c644d2c95ba'
    parsed_id2 = '4c0c865f-3012-4d02-8560-5c644d2c95ba'
    parsed_is_calltracking = False
    offer_is_calltracking = True
    await pg.execute("""
        INSERT INTO offers_for_call (
            id, parsed_id, client_id, priority, publication_status,status,category,created_at,synced_at,is_calltracking
        ) VALUES
        (2, $1, 2, 1, 'Draft', 'draft', 'flatRent', 'now()', 'now()', $2);
    """, [parsed_id1, offer_is_calltracking])
    old_offer_data = {
        'phones': ['87771114422'],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'address': 'адресф'
    }
    old_data = {
        'id': parsed_id1,
        'sourceGroupId': 'source_group_id_example1',
        'sourceObjectId': source_object_id,
        'sourceUserId': '27d1a87eb7a7cda52167530e424ca317',
        'userSegment': 'c',
        'userSubsegment': 'subsegment_example_1',
        'isCalltracking': parsed_is_calltracking,
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
        'id': parsed_id2,
        'sourceGroupId': 'source_group_id_example1',
        'sourceObjectId': source_object_id,
        'sourceUserId': '27d1a87eb7a7cda52167530e424ca317',
        'userSegment': 'c',
        'userSubsegment': 'subsegment_example_1',
        'isCalltracking': parsed_is_calltracking,
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

    # assert
    offer_row = await pg.fetchrow('SELECT * FROM offers_for_call where parsed_id=$1', [parsed_id1])
    assert offer_row['is_calltracking'] == parsed_is_calltracking

    row = await pg.fetchrow('SELECT * FROM parsed_offers LIMIT 1')
    row.pop('timestamp')
    row.pop('created_at')
    row.pop('updated_at')
    assert row == {
        'id': parsed_id1,
        'user_segment': 'c',
        'user_subsegment': 'subsegment_example_1',
        'source_object_id': source_object_id,
        'source_user_id': '27d1a87eb7a7cda52167530e424ca317',
        'source_object_model': (
            '{"title": "название новое", "phones": ["87771114422"], '
            '"region": 4628, "address": "адрес новый", "category": "flatSale", '
            '"description": "описание новое"}'
        ),
        'is_calltracking': False,
        'synced': False,
        'is_test': False,
        'source_group_id': 'source_group_id_example1',
        'external_offer_type': None,
    }
