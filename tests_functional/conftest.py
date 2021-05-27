# pylint: disable=redefined-outer-name

from asyncio import sleep
from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope='session')
async def start(pg):
    await pg.execute_scripts((Path('contrib') / 'postgresql' / 'migrations').glob('*.sql'))


@pytest.fixture(name='pg', scope='session')
async def pg_fixture(postgres_service):
    yield await postgres_service.get_database_by_alias('external_offers')


@pytest.fixture
def pages_folder():
    return Path('tests_functional') / 'data' / 'pages'


@pytest.fixture
def database_fixture_folder():
    return Path('tests_functional') / 'data' / 'fixtures'


@pytest.fixture
def offers_and_clients_fixture(database_fixture_folder):
    return database_fixture_folder / 'offers_and_clients.sql'


@pytest.fixture
def parsed_offers_fixture(database_fixture_folder):
    return database_fixture_folder / 'parsed_offers.sql'


@pytest.fixture
def parsed_offers_fixture_for_clients_test(database_fixture_folder):
    return database_fixture_folder / 'parsed_offers_for_clients_test.sql'


@pytest.fixture
def parsed_offers_fixture_for_offers_for_call_test(database_fixture_folder):
    return database_fixture_folder / 'parsed_offers_for_offers_for_call_test.sql'


@pytest.fixture
def admin_external_offers_operator_without_client_html(pages_folder):
    return (pages_folder /
            'admin_external_offers_operator_without_client.html')


@pytest.fixture
def admin_external_offers_operator_with_client_in_progress_html(pages_folder):
    return (pages_folder /
            'admin_external_offers_operator_with_client_in_progress.html')


@pytest.fixture
def admin_external_offers_operator_with_client_cancelled_html(pages_folder):
    return (pages_folder /
            'admin_external_offers_operator_with_client_cancelled.html')


@pytest.fixture(scope='session')
async def users_mock(http_mock_service):
    yield await http_mock_service.make_microservice_mock('users')


@pytest.fixture(scope='session')
async def monolith_cian_service_mock(http_mock_service):
    yield await http_mock_service.make_microservice_mock('monolith-cian-service')


@pytest.fixture(scope='session')
async def monolith_cian_announcementapi_mock(http_mock_service):
    yield await http_mock_service.make_microservice_mock('monolith-cian-announcementapi')


@pytest.fixture(scope='session')
async def monolith_cian_profileapi_mock(http_mock_service):
    yield await http_mock_service.make_microservice_mock('monolith-cian-profileapi')


@pytest.fixture(scope='session')
async def monolith_cian_geoapi_mock(http_mock_service):
    yield await http_mock_service.make_microservice_mock('monolith-cian-geoapi')


@pytest.fixture(scope='session')
async def monolith_cian_realty_mock(http_mock_service):
    yield await http_mock_service.make_microservice_mock('monolith-cian-realty')


@pytest.fixture(scope='session')
async def announcements_mock(http_mock_service):
    yield await http_mock_service.make_microservice_mock('announcements')


@pytest.fixture(scope='session')
async def send_parsed_offer_consumer(runner):
    await runner.start_background_python_command('send-parsed-offers')
    await sleep(4)


@pytest.fixture(scope='session')
async def save_parsed_offer_consumer(runner):
    await runner.start_background_python_command('save-parsed-offers')
    await sleep(4)


@pytest.fixture
async def save_offer_request_body():
    return {
        'dealType': 'rent',
        'offerType': 'flat',
        'termType': 'long',
        'category': 'room',
        'address': 'ул. просторная 6, квартира 200',
        'realtyType': 'apartments',
        'totalArea': 120,
        'rooms_count': None,
        'floor_number': 1,
        'floors_count': 5,
        'price': 100000,
        'saleType': '',
        'offerId': '1',
        'clientId': '7',
        'description': 'Test'
    }


@pytest.fixture
async def save_offer_request_body_with_create_new_account(save_offer_request_body):
    save_offer_request_body['createNewAccount'] = True
    return save_offer_request_body


@pytest.fixture
async def save_offer_request_body_for_suburban():
    return {
        'dealType': 'sale',
        'offerType': 'suburban',
        'category': 'land',
        'address': 'ул. просторная 6, квартира 200',
        'realtyType': None,
        'totalArea': 120,
        'rooms_count': None,
        'floor_number': None,
        'floors_count': None,
        'price': 100000,
        'saleType': '',
        'offerId': '1',
        'clientId': '7',
        'description': 'Test',
        'landArea': 6.0,
        'areaUnitType': 'sotka',
    }
