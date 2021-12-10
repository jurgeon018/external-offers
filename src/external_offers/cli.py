import click
from cian_core.kafka import register_kafka_consumer
from cian_core.rabbitmq.consumer_cli import register_consumer
from cian_core.web import Application
from tornado.ioloop import IOLoop

from external_offers import entities, setup
from external_offers.queue.consumers import process_announcement_callback, save_parsed_offers_callback
from external_offers.queue.queues import process_announcements_queue
from external_offers.queue.schemas import RabbitMQAnnouncementMessageSchema
from external_offers.services.clear_outdated_offers import clear_outdated_offers
from external_offers.services.offers_creator import sync_and_create_offers, create_phones_statuses
from external_offers.services.send_clients_to_kafka import send_clients_to_kafka
from external_offers.services.send_event_logs_to_kafka import send_event_logs_to_kafka
from external_offers.services.send_latest_timestamp_to_graphite import send_parsed_offers_timestamp_diff_to_graphite
from external_offers.services.send_offers_and_clients_to_grafana import (
    send_processed_offers_and_clients_amount_to_grafana,
    send_waiting_offers_and_clients_amount_to_grafana,
)
from external_offers.services.send_offers_for_call_to_kafka import send_offers_for_call_to_kafka
from external_offers.services.send_operators_to_kafka import send_operators_to_kafka
from external_offers.services.send_parsed_offers_to_kafka import send_parsed_offers_to_kafka
from external_offers.services.send_teams_to_kafka import send_teams_to_kafka
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
    IOLoop.current().run_sync(sync_and_create_offers)


@cli.command
def create_phones_statuses_cron():
    """ Закешировать информацию про ЛК клиентов по номеру телефона """
    IOLoop.current().run_sync(create_phones_statuses)


@cli.command()
def clear_outdated_offers_cron():
    """ Очистить таблицу спаршенных объявлений и очередь от неактуальных объявлений """
    IOLoop.current().run_sync(clear_outdated_offers)


@cli.command()
def send_latest_parsed_offers_timestamp_diff_to_graphite():
    """ Отправить в grafana разницу между now() и timestamp последнего пришедшего спаршенного объявления """
    IOLoop.current().run_sync(send_parsed_offers_timestamp_diff_to_graphite)


@cli.command()
def send_waiting_offers_and_clients_amount_to_grafana_cron():
    """ Отправить в grafana количество заданий в ожидании и клиентов в ожидании в очереди в начале дня """
    IOLoop.current().run_sync(send_waiting_offers_and_clients_amount_to_grafana)


@cli.command()
def send_processed_offers_and_clients_amount_to_grafana_cron():
    """ Отправить в grafana количество заданий и клиентов которых взяли в работу за день """
    IOLoop.current().run_sync(send_processed_offers_and_clients_amount_to_grafana)


@cli.command()
def send_parsed_offers_to_kafka_cron():
    """ Отправить записи из таблицы parsed_offers в кафку """
    IOLoop.current().run_sync(send_parsed_offers_to_kafka)


@cli.command()
def send_offers_for_call_to_kafka_cron():
    """ Отправить записи из таблицы offers_for_call в кафку """
    IOLoop.current().run_sync(send_offers_for_call_to_kafka)


@cli.command()
def send_operators_to_kafka_cron():
    """ Отправить записи из таблицы operators в кафку """
    IOLoop.current().run_sync(send_operators_to_kafka)


@cli.command()
def send_teams_to_kafka_cron():
    """ Отправить записи из таблицы teams в кафку """
    IOLoop.current().run_sync(send_teams_to_kafka)


@cli.command()
def send_event_logs_to_kafka_cron():
    """ Отправить записи из таблицы event_log в кафку """
    IOLoop.current().run_sync(send_event_logs_to_kafka)


@cli.command()
def send_clients_to_kafka_cron():
    """ Отправить записи из таблицы clients в кафку """
    IOLoop.current().run_sync(send_clients_to_kafka)


# [ML] сохранение объявлений с внешних площадок
register_kafka_consumer(
    command=cli.command('save-parsed-offers'),
    topic='ml-content-copying.change',
    group_id='external-offers.save-external-offers',
    callback=save_parsed_offers_callback,
    default_max_bulk_size=25,
    message_type=entities.ParsedOfferMessage
)


# [announcements] обновляет объявление
register_consumer(
    command=cli.command('process_announcement_consumer'),
    queue=process_announcements_queue,
    callback=process_announcement_callback,
    schema_cls=RabbitMQAnnouncementMessageSchema,
    dead_queue_enabled=True,
)
