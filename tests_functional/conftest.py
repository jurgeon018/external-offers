from pathlib import Path

import pytest


@pytest.fixture(autouse=True, scope='session')
async def start(pg, runner, global_runtime_settings):
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
