import click
from cian_core.kafka import register_kafka_consumer
from cian_core.web import Application
from tornado.ioloop import IOLoop

from external_offers import entities, setup
from external_offers.queue.consumers import save_parsed_offers_callback, send_change_event
from external_offers.services.clear_outdated_offers import clear_outdated_offers
from external_offers.services.offers_creator import sync_offers_for_call_with_parsed
from external_offers.services.send_latest_timestamp_to_graphite import send_parsed_offers_timestamp_diff_to_graphite
from external_offers.services.send_offers_for_call_to_kafka import send_offers_for_call_to_kafka
from external_offers.services.send_parsed_offers_to_kafka import send_parsed_offers_to_kafka
from external_offers.services.send_offers_for_call_to_grafana import 
from external_offers.web.urls import urlpatterns


@click.group()
def cli() -> None:
    setup()


@cli.command()
@click.option('--debug', is_flag=True)
@click.option('--host', type=str, default='127.0.0.1')
@click.option('--port', type=int, default=8000)
def serve(debug: bool, host: str, port: int) -> None:
    app = Application(urlpatterns, debug=debug)
    app.start(host=host, port=port)


@cli.command()
def create_offers_for_call():
    """ Синхронизировать таблицы offers_for_call и clients на основе parsed_offers """
    IOLoop.current().run_sync(sync_offers_for_call_with_parsed)


@cli.command()
def clear_outdated_offers_cron():
    """ Очистить таблицу спаршенных объявлений и очередь от неактуальных объявлений """
    IOLoop.current().run_sync(clear_outdated_offers)


@cli.command()
def send_latest_parsed_offers_timestamp_diff_to_graphite():
    """ Отправить в grafana разницу между now() и timestamp последнего пришедшего спаршенного объявления """
    IOLoop.current().run_sync(send_parsed_offers_timestamp_diff_to_graphite)


async def send_waiting_offers_and_clients_amount_to_grafana():
    from cian_core.statsd import statsd
    from external_offers.repositories.postgresql.offers import (
        sync_waiting_clients_with_grafana,
        sync_waiting_offers_with_grafana,
    )
    waiting_clients_count = await sync_waiting_clients_with_grafana()
    waiting_offers_count = await sync_waiting_offers_with_grafana()
    print('waiting_clients_count', waiting_clients_count)
    print('waiting_offers_count', waiting_offers_count)
    # statsd.incr('waiting_clients.count', count=waiting_clients_count)
    # statsd.incr('waiting_offers.count', count=waiting_offers_count)


async def send_in_progress_offers_and_clients_amount_to_grafana():
    from cian_core.statsd import statsd
    from external_offers import pg
    from external_offers.repositories.postgresql.offers import (
        get_synced_offers_count,
        get_synced_clients_count,
        get_non_waiting_synced_offers_count,
        get_non_waiting_synced_clients_count,
        unsync_clients_with_grafana,
        unsync_offers_with_grafana,
    )

    synced_offers_count = await get_synced_offers_count()
    synced_clients_count = await get_synced_clients_count()
    non_waiting_synced_offers_count = await get_non_waiting_synced_offers_count()
    non_waiting_synced_clients_count = await get_non_waiting_synced_clients_count()

    # non_waiting_synced_offers_percentage = non_waiting_synced_offers_count / synced_offers_count * 100
    # non_waiting_synced_clients_percentage = non_waiting_synced_clients_count / synced_clients_count * 100
    print("synced_offers_count: ", synced_offers_count)
    print("synced_clients_count: ", synced_clients_count)
    print("non_waiting_synced_offers_count: ", non_waiting_synced_offers_count)
    print("non_waiting_synced_clients_count: ", non_waiting_synced_clients_count)
    # print("non_waiting_synced_offers_percentage: ", non_waiting_synced_offers_percentage)
    # print("non_waiting_synced_clients_percentage: ", non_waiting_synced_clients_percentage)
    # statsd.incr('non_waiting_offers.count', count=non_waiting_synced_offers_count)
    # statsd.incr('non_waiting_synced_clients.count', count=non_waiting_synced_clients_count)
    # statsd.incr('non_waiting_offers.percentage', count=non_waiting_synced_offers_percentage)
    # statsd.incr('non_waiting_synced_clients.percentage', count=non_waiting_synced_clients_percentage)
    await unsync_clients_with_grafana()
    await unsync_offers_with_grafana()


@cli.command()
def send_waiting_offers_and_clients_amount_to_grafana_cron():
    """ Отправить в grafana количество заданий в ожидании и клиентов в ожидании в очереди в начале дня """
    IOLoop.current().run_sync(send_waiting_offers_and_clients_amount_to_grafana)


@cli.command()
def send_in_progress_offers_and_clients_amount_to_grafana_cron():
    """ Отправить в grafana количество заданий и клиентов которых взяли в работу за день """
    IOLoop.current().run_sync(send_in_progress_offers_and_clients_amount_to_grafana)


@cli.command()
def send_parsed_offers_to_kafka_cron():
    """ Отправить записи из таблицы parsed_offers в кафку """
    IOLoop.current().run_sync(send_parsed_offers_to_kafka)


@cli.command()
def send_offers_for_call_to_kafka_cron():
    """ Отправить записи из таблицы offers_for_call в кафку """
    IOLoop.current().run_sync(send_offers_for_call_to_kafka)


# [ML] сохранение объявлений с внешних площадок
register_kafka_consumer(
    command=cli.command('save-parsed-offers'),
    topic='ml-content-copying.change',
    group_id='external-offers.save-external-offers',
    callback=save_parsed_offers_callback,
    default_max_bulk_size=25,
    message_type=entities.ParsedOfferMessage
)


# [ML] преобразовать объявления с внешних площадок в object_model и оповестить
register_kafka_consumer(
    command=cli.command('send-parsed-offers'),
    topic='ml-content-copying.change',
    group_id='external-offers.transform-external-offers',
    callback=send_change_event,
    default_max_bulk_size=25,
    message_type=entities.ParsedOfferMessage
)
