import pytest
from cian_core.postgres import PostgresConnection
from cian_test_utils import future
from tornado import web

from external_offers import pg
from external_offers.web.urls import urlpatterns


@pytest.fixture
def app():
    return web.Application(urlpatterns)


@pytest.fixture(name='postgres')
def postgres_connection_fixture(mocker):  # pylint: disable=redefined-outer-name
    connection = mocker.Mock(spec=PostgresConnection)
    connection.execute.return_value = future()
    connection.fetch.return_value = future([])
    connection.fetchrow.return_value = future()
    connection.fetchval.return_value = future(1)
    mocker.patch.object(pg, 'get', return_value=connection)

    return connection
