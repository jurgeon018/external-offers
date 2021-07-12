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


async def send_waiting_offers_and_clients_amount_to_grahite():
    from cian_core.statsd import statsd
    from external_offers.repositories.postgresql.offers import (
        sync_waiting_clients_with_grafana,
        sync_waiting_offers_with_grafana,
    )

    # TODO: ?? перенести из крона в sync_offers_for_call_with_parsed
    # после clear_and_prioritize_waiting_offers()??
    waiting_clients = await sync_waiting_clients_with_grafana()
    waiting_offers = await sync_waiting_offers_with_grafana()
    waiting_clients_count = len(waiting_clients)
    waiting_offers_count = len(waiting_offers)
    statsd.incr('waiting_clients.count', count=waiting_clients_count)
    statsd.incr('waiting_offers.count', count=waiting_offers_count)


async def send_in_progress_offers_and_clients_amount_to_graphite():
    from cian_core.statsd import statsd
    # TODO: ?? перенести из крона в update_offers_list
    # в то место в котором клиент и задание присваиваются оператору?

    non_waiting_offers_count = ...
    non_waiting_clients_count = ...
    non_waiting_offers_percentage = ...
    non_waiting_clients_percentage = ...

    statsd.incr('non_waiting_offers.count', count=non_waiting_offers_count)
    statsd.incr('non_waiting_clients.count', count=non_waiting_clients_count)
    statsd.incr('non_waiting_offers.percentage', count=non_waiting_offers_percentage)
    statsd.incr('non_waiting_clients.percentage', count=non_waiting_clients_percentage)


@cli.command()
def send_waiting_offers_and_clients_amount_to_grahite_cron():
    """ Отправить в grafana количество заданий в ожидании и клиентов в ожидании в очереди в начале дня """
    IOLoop.current().run_sync(send_waiting_offers_and_clients_amount_to_grahite)


@cli.command()
def send_in_progress_offers_and_clients_amount_to_graphite_cron():
    """ Отправить в grafana количество заданий и клиентов которых взяли в работу за день """
    IOLoop.current().run_sync(send_in_progress_offers_and_clients_amount_to_graphite)


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
