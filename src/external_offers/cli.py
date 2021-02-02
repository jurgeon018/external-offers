from functools import partial
from typing import Optional

import click
from cian_core.kafka import register_kafka_consumer
from cian_core.web import Application
from tornado.ioloop import IOLoop

from external_offers import entities, setup
from external_offers.queue.consumers import save_parsed_offers_callback, send_change_event
from external_offers.services.clear_outdated_offers import clear_outdated_offers
from external_offers.services.offers_creator import sync_offers_for_call_with_parsed
from external_offers.services.send_latest_timestamp_to_graphite import send_parsed_offers_timestamp_diff_to_graphite
from external_offers.services.sync_event_log import sync_event_log
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


@cli.command()
@click.option('--date-from', type=str, default=None)
@click.option('--date-to', type=str, default=None)
def sync_event_log_with_kafka_analytics(date_from: Optional[str], date_to: Optional[str]):
    """ Дослать события аналитики за период на основе таблицы event_log  """
    IOLoop.current().run_sync(partial(sync_event_log, date_from, date_to))


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
