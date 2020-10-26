import cian_core
from cian_core.postgres import PostgresConnection
from cian_core.registry import postgres_connections
from cian_core.registry.base import Value


pg: 'Value[PostgresConnection]' = postgres_connections('external_offers')


def setup() -> None:
    cian_core.setup(
        options=cian_core.Options(
            setup_postgres=True,
            setup_kafka=True
        ),
    )
