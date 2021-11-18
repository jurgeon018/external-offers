# pylint: disable=redefined-outer-name

from asyncio import sleep
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse


@pytest.fixture(autouse=True, scope='session')
async def start(pg, runner):
    await pg.execute_scripts((Path('contrib') / 'postgresql' / 'migrations').glob('*.sql'))
    await runner.start_background_python_command('process_announcement_consumer')


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
def parsed_offers_fixture_for_unactivated_clients(database_fixture_folder):
    return database_fixture_folder / 'parsed_offers_fixture_for_unactivated_clients.sql'


@pytest.fixture
def parsed_offers_fixture_for_offers_for_call_test(database_fixture_folder):
    return database_fixture_folder / 'parsed_offers_for_offers_for_call_test.sql'


@pytest.fixture
def parsed_offers_for_teams(database_fixture_folder):
    return database_fixture_folder / 'parsed_offers_for_teams.sql'


@pytest.fixture
def segmentation_rows_fixture(database_fixture_folder):
    return database_fixture_folder / 'segmentation_rows.sql'


@pytest.fixture
def teams_fixture(database_fixture_folder):
    return database_fixture_folder / 'teams.sql'


@pytest.fixture
def test_objects_fixture(database_fixture_folder):
    return database_fixture_folder / 'test_objects.sql'


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
async def sms_mock(http_mock_service):
    yield await http_mock_service.make_microservice_mock('sms')


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
        'landStatus': 'individualHousingConstruction'
    }


def v2_get_users_by_phone_response(minutes):
    creationDate = datetime.utcnow() - timedelta(minutes=minutes)
    creationDate = datetime.strftime(creationDate, '%Y-%m-%d %H:%M:%S.%f')
    return {'users': [{
        'id': 12835367,
        'cianUserId': 12835367,
        'mainAnnouncementsRegionId': 2,
        'email': 'forias@yandex.ru',
        'state': 'active',
        'stateChangeReason': None,
        'secretCode': '8321',
        'birthday': '0001-01-01T00:00:00+02:31',
        'firstName': 'Александровна',
        'lastName': 'Ирина',
        'city': None,
        'userName': None,
        'creationDate': creationDate,
        'ip': 167772335,
        'externalUserSourceType': None,
        'isAgent': False
    }]}


@pytest.fixture
async def get_recent_users_by_phone_mock(
    users_mock,
    runtime_settings,
):
    minutes = 120 - 1

    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body=v2_get_users_by_phone_response(minutes)
        ),
    )


@pytest.fixture
async def get_old_users_by_phone_mock(
    users_mock,
    runtime_settings,
):
    minutes = 120 + 1

    stub = await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body=v2_get_users_by_phone_response(minutes)
        ),
    )
    return stub
