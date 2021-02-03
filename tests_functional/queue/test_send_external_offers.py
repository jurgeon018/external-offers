import asyncio

import pytest
from cian_functional_test_utils import DependencyType
from cian_functional_test_utils.pytest_plugin import KafkaService, MockResponse, Runner
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

    await runner.start_background_python_command('send-parsed-offers')


async def test_external_offer_callback__new_external_offer__send_publish_message(
    kafka_service,
    queue_service,
    monolith_cian_geoapi_mock,
    runtime_settings,
):
    # arrange
    await runtime_settings.set({
        'SUITABLE_CATEGORIES_FOR_REPORTING': ['flatSale'],
    })

    offer_data = {
        'phones': ['87771114422'],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'address': 'адресф',
        'lat': 1.0,
        'lng': 2.0,
        'url': 'http://test',
        'floorNumber': 3,
        'roomsCount': 5,
        'totalArea': 30,
        'floorsCount': 10
    }
    data = {
        'id': '3c0c865f-3012-4d02-8560-5c644d2c95ba',
        'sourceObjectId': '1_1986816313',
        'sourceUserId': '27d1a87eb7a7cda52167530e424ca317',
        'userSegment': 'c',
        'isCalltracking': False,
        'sourceObjectModel': offer_data,
        'timestamp': '2020-10-26T13:55:00+00:00'
    }
    queue = await queue_service.make_tmp_queue(
        routing_key='external-offers.offers-reporting.v1.changed',
    )
    await monolith_cian_geoapi_mock.add_stub(
        method='POST',
        path='/v2/geocode/',
        response=MockResponse(
            body={
                'country_id': 1233,
                'location_path': [1],
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': []
            }
        ),
    )

    # act
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=data
    )
    await asyncio.sleep(2)

    # assert
    messages = await queue.get_messages()
    assert len(messages) == 1

    payload = messages[0].payload
    assert payload['sourceModel'] == {
        'source': 'avito',
        'sourceObjectId': '1_1986816313',
        'timestamp': '2020-10-26T13:55:00+00:00',
        'externalUrl': 'http://test'
    }

    assert payload['model']['category'] == 'flatSale'
    assert payload['model']['floorNumber'] == 3
    assert payload['model']['roomsCount'] == 5
    assert payload['model']['totalArea'] == 30
    assert payload['model']['description'] == 'описание'
    assert not payload['model']['isEnabledCallTracking']

    assert payload['model']['building']['floorsCount'] == 10

    assert payload['model']['phones'] == [{
            'number': '7771114422',
            'countryCode': '+7',
            'sourcePhone': None
    }]


async def test_external_offer_callback__new_external_offer_with_coordinates__geoapi_called(
    kafka_service,
    queue_service,
    monolith_cian_geoapi_mock,
    runtime_settings,
):
    # arrange
    await runtime_settings.set({
        'SUITABLE_CATEGORIES_FOR_REPORTING': ['flatSale'],
    })

    offer_data = {
        'phones': ['87771114422'],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'address': 'адресф',
        'lat': 1.0,
        'lng': 2.0
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
    await queue_service.make_tmp_queue(
        routing_key='external-offers.offers-reporting.v1.changed',
    )
    geoapi_stub = await monolith_cian_geoapi_mock.add_stub(
        method='POST',
        path='/v2/geocode/',
        response=MockResponse(
            status=400
        ),
    )

    # act
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=data
    )
    await asyncio.sleep(2)

    # assert
    request = await geoapi_stub.get_request()
    assert request.body == b'{"address":null,"kind":"house","lat":1.0,"lng":2.0}'


async def test_external_offer_callback__new_external_offer_without_lat__geoapi_not_called(
    kafka_service,
    monolith_cian_geoapi_mock,
    runtime_settings,
):
    # arrange
    await runtime_settings.set({
        'SUITABLE_CATEGORIES_FOR_REPORTING': ['flatSale'],
    })

    offer_data = {
        'phones': ['87771114422'],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'address': 'адресф',
        'lat': None,
        'lng': 2.0
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

    geoapi_stub = await monolith_cian_geoapi_mock.add_stub(
        method='POST',
        path='/v2/geocode/',
        response=MockResponse(
            status=400
        ),
    )

    # act
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=data
    )
    await asyncio.sleep(2)

    # assert
    with pytest.raises(AssertionError):
        await geoapi_stub.get_request()


async def test_external_offer_callback__new_external_offer_without_lng__geoapi_not_called(
    kafka_service,
    monolith_cian_geoapi_mock,
    runtime_settings,
):
    # arrange
    await runtime_settings.set({
        'SUITABLE_CATEGORIES_FOR_REPORTING': ['flatSale'],
    })

    offer_data = {
        'phones': ['87771114422'],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'address': 'адресф',
        'lat': 1.0,
        'lng': None
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
    geoapi_stub = await monolith_cian_geoapi_mock.add_stub(
        method='POST',
        path='/v2/geocode/',
        response=MockResponse(
            status=400
        ),
    )

    # act
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=data
    )
    await asyncio.sleep(2)

    # assert
    with pytest.raises(AssertionError):
        await geoapi_stub.get_request()


async def test_external_offer_callback__new_external_offer_without_phones__no_message(
    kafka_service,
    queue_service,
    runtime_settings,
):
    # arrange
    await runtime_settings.set({
        'SUITABLE_CATEGORIES_FOR_REPORTING': ['flatSale'],
    })

    offer_data = {
        'phones': [],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'address': 'адресф',
        'lat': 1.0,
        'lng': None
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
    queue = await queue_service.make_tmp_queue(
        routing_key='external-offers.offers-reporting.v1.changed',
    )

    # act
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=data
    )
    await asyncio.sleep(2)

    # assert
    messages = await queue.get_messages()
    assert len(messages) == 0


async def test_external_offer_callback__new_external_offer_nonsuitable_category__no_message(
    kafka_service,
    queue_service,
    runtime_settings
):
    # arrange
    await runtime_settings.set({
        'SUITABLE_CATEGORIES_FOR_REPORTING': ['commercialSale'],
    })

    offer_data = {
        'phones': [],
        'category': 'flatSale',
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'address': 'адресф',
        'lat': 1.0,
        'lng': None
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
    queue = await queue_service.make_tmp_queue(
        routing_key='external-offers.offers-reporting.v1.changed',
    )

    # act
    await kafka_service.publish(
        topic='ml-content-copying.change',
        message=data
    )
    await asyncio.sleep(2)

    # assert
    messages = await queue.get_messages()
    assert len(messages) == 0