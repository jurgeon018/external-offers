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


@pytest.mark.parametrize(
    'category',
    ['flatSale', 'newBuildingFlatSale']
)
async def test_external_offer_callback__new_external_offer__send_publish_message(
    kafka_service,
    queue_service,
    monolith_cian_geoapi_mock,
    monolith_cian_realty_mock,
    category,
    runtime_settings,
):
    # arrange
    await runtime_settings.set({
        'SUITABLE_CATEGORIES_FOR_REPORTING': ['flatSale', 'newBuildingFlatSale'],
        'MAX_GEOCODE_STATIONS': 3,
        'SUITABLE_EXTERNAL_SOURCES_FOR_SEND': ['8']
    })

    offer_data = {
        'phones': ['87771114422'],
        'category': category,
        'region': 4628,
        'title': 'название',
        'description': 'описание',
        'updateDate': '2021-12-29T09:13:08.965324+00:00',
        'isAgency': False,
        'address': 'адрес',
        'lat': 12.0,
        'lng': 13.0,
        'url': 'http://test',
        'floorNumber': 3,
        'roomsCount': 5,
        'totalArea': 30,
        'floorsCount': 10
    }
    data = {
        'id': '3c0c865f-3012-4d02-8560-5c644d2c95ba',
        'sourceObjectId': '8_1986816313',
        'sourceUserId': '27d1a87eb7a7cda52167530e424ca317',
        'userSegment': 'c',
        'isCalltracking': False,
        'sourceObjectModel': offer_data,
        'timestamp': '2020-10-26T13:55:00+00:00'
    }
    parent_district_id = 6
    queue = await queue_service.make_tmp_queue(
        routing_key='external-offers.offers-reporting.v1.changed',
    )
    await monolith_cian_geoapi_mock.add_stub(
        method='POST',
        path='/v2/geocode/',
        response=MockResponse(
            body={
                'countryId': 1233,
                'locationPath': [1],
                'geo': {
                    'lat': 12.0,
                    'lng': 13.0
                },
                'details': [
                    {
                        'id': 1,
                        'fullName': 'Область test',
                        'name': 'test',
                        'isLocality': False,
                        'geoType': 'Location',
                    }, {
                        'id': 2,
                        'fullName': 'Город test',
                        'name': 'test',
                        'isLocality': True,
                        'geoType': 'Location',
                    }, {
                        'id': 3,
                        'fullName': 'Улица test',
                        'name': 'test',
                        'isLocality': False,
                        'geoType': 'Street',
                    }, {
                        'id': 4,
                        'fullName': '27',
                        'name': '27',
                        'isLocality': False,
                        'geoType': 'House',
                    }
                ]
            }
        ),
    )
    await monolith_cian_geoapi_mock.add_stub(
        method='GET',
        path='/v1/get-districts-by-child/',
        response=MockResponse(
            body=[{
                'id': 4,
                'locationId': 5,
                'name': 'Черная речка',
                'parentId': parent_district_id,
                'type': 'Okrug',
            }, {
                'id': 5,
                'locationId': 7,
                'name': 'Тестовый',
                'parentId': None,
                'type': 'Okrug',
            }]
        )
    )

    get_districts_by_ids_stub = await monolith_cian_geoapi_mock.add_stub(
        method='GET',
        path='/v1/get-districts-by-ids/',
        response=MockResponse(
            body=[{
                'id': parent_district_id,
                'locationId': 2,
                'name': 'Приморский',
                'parentId': None,
                'type': 'Raion',
            }]
        )
    )

    await monolith_cian_geoapi_mock.add_stub(
        method='GET',
        path='/v2/undergrounds/get-all/',
        response=MockResponse(
            body=[{
                'cianId': 85,
                'entrances': [
                    {'id': 3, 'lat': 55.752408, 'lng': 37.717001, 'name': '1'},
                    {'id': 859, 'lat': 55.753528, 'lng': 37.719145, 'name': '2'}
                ],
                'id': 1,
                'isPutIntoOperation': True,
                'lat': 12.0,
                'lines': [
                    {'lineColor': 'FFDF00', 'lineId': 4, 'lineName': 'Калининско-Солнцевская'},
                    {'lineColor': '7ACDCE', 'lineId': 27, 'lineName': 'Большая кольцевая линия'}
                ],
                'lng': 13.0,
                'locationId': 1,
                'name': 'Авиамоторная1',
                'translitName': 'aviamotornaya'
            }, {
                'cianId': 85,
                'entrances': [
                    {'id': 3, 'lat': 55.752408, 'lng': 37.717001, 'name': '1'},
                    {'id': 859, 'lat': 55.753528, 'lng': 37.719145, 'name': '2'}
                ],
                'id': 1,
                'isPutIntoOperation': True,
                'lat': 100.0,
                'lines': [
                    {'lineColor': 'FFDF00', 'lineId': 4, 'lineName': 'Калининско-Солнцевская'},
                    {'lineColor': '7ACDCE', 'lineId': 27, 'lineName': 'Большая кольцевая линия'}
                ],
                'lng': 100.0,
                'locationId': 1,
                'name': 'Авиамоторная',
                'translitName': 'aviamotornaya'
            }, {
                'cianId': 85,
                'entrances': [
                    {'id': 3, 'lat': 55.752408, 'lng': 37.717001, 'name': '1'},
                    {'id': 859, 'lat': 55.753528, 'lng': 37.719145, 'name': '2'}
                ],
                'id': 1,
                'isPutIntoOperation': True,
                'lat': 12.0,
                'lines': [
                    {'lineColor': 'FFDF00', 'lineId': 4, 'lineName': 'Калининско-Солнцевская'},
                    {'lineColor': '7ACDCE', 'lineId': 27, 'lineName': 'Большая кольцевая линия'}
                ],
                'lng': 13.0,
                'locationId': 1,
                'name': 'станция Авиамоторная2',
                'translitName': 'aviamotornaya'
            }, {
                'cianId': 85,
                'entrances': [
                    {'id': 3, 'lat': 55.752408, 'lng': 37.717001, 'name': '1'},
                    {'id': 859, 'lat': 55.753528, 'lng': 37.719145, 'name': '2'}
                ],
                'id': 1,
                'isPutIntoOperation': True,
                'lat': 12.0,
                'lines': [
                    {'lineColor': 'FFDF00', 'lineId': 4, 'lineName': 'Калининско-Солнцевская'},
                    {'lineColor': '7ACDCE', 'lineId': 27, 'lineName': 'Большая кольцевая линия'}
                ],
                'lng': 13.0,
                'locationId': 1,
                'name': 'Авиамоторная2',
                'translitName': 'aviamotornaya'
            }]
        ),
    )

    await monolith_cian_realty_mock.add_stub(
        method='GET',
        path='/api/autocomplete-undeground/',
        response=[MockResponse(
            body=[{
                'color': 'test',
                'id': 1,
                'name': 'Авиамоторная1',
                'timeByCar': None,
                'timeByWalk': 5,
            }],
        ), MockResponse(
            body=[{
                'color': 'test',
                'id': 1,
                'name': 'Авиамоторная2',
                'timeByCar': 5,
                'timeByWalk': None,
            }],
        ), MockResponse(
            body=[{
                'color': 'test',
                'id': 1,
                'name': 'Авиамоторная3',
                'timeByCar': 5,
                'timeByWalk': None,
            }],
        )],
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
    request = await get_districts_by_ids_stub.get_request()

    assert request.params['ids'] == f'{parent_district_id}'

    assert payload['sourceModel'] == {
        'source': 'yandex',
        'sourceObjectId': '8_1986816313',
        'timestamp': '2020-10-26T13:55:00+00:00',
        'externalUrl': 'http://test'
    }

    assert payload['model']['category'] == category
    assert payload['model']['floorNumber'] == 3
    assert payload['model']['flatType'] == 'rooms'
    assert payload['model']['roomsCount'] == 5
    assert payload['model']['totalArea'] == 30
    assert payload['model']['description'] == 'описание'
    assert not payload['model']['isEnabledCallTracking']
    assert payload['model']['isByHomeOwner']
    assert payload['model']['editDate'] == '2021-12-29T09:13:08.965324+00:00'
    assert payload['model']['geo']['userInput'] == 'адрес'
    assert payload['model']['geo']['address'] == [{
        'id': 1,
        'name': 'test',
        'fullName': 'Область test',
        'isFormingAddress': True,
        'shortName': 'test',
        'locationTypeId': 2,
        'type': 'location'
    }, {
        'id': 2,
        'name': 'test',
        'fullName': 'Город test',
        'isFormingAddress': True,
        'shortName': 'test',
        'locationTypeId': 1,
        'type': 'location'
    }, {
        'id': 3,
        'name': 'test',
        'fullName': 'Улица test',
        'isFormingAddress': True,
        'shortName': 'test',
        'type': 'street'
    }, {
        'id': 4,
        'fullName': '27',
        'name': '27',
        'isFormingAddress': True,
        'shortName': '27',
        'type': 'house',
    }]
    assert payload['model']['geo']['district'] == [
        {
            'id': 4,
            'locationId': 5,
            'name': 'Черная речка',
            'parentId': parent_district_id,
            'type': 'okrug'
        }, {
            'id': 5,
            'locationId': 7,
            'name': 'Тестовый',
            'type': 'okrug'
        },  {
            'id': parent_district_id,
            'locationId': 2,
            'name': 'Приморский',
            'type': 'raion'
        }
    ]
    assert payload['model']['building']['floorsCount'] == 10

    assert payload['model']['phones'] == [{
            'number': '7771114422',
            'countryCode': '+7',
    }]
