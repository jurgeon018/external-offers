from functools import partial

import click
from cian_core.kafka import register_kafka_consumer
from cian_core.web import Application
from tornado.ioloop import IOLoop

from external_offers import entities, setup
from external_offers.queue.consumers import save_parsed_offers_callback
from external_offers.services.offers_creator import sync_offers_for_call_with_parsed
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
    """ Синхронизировать таблицы offers_for_call и clients на основе parsed_offers"""

    IOLoop.current().run_sync(partial(sync_offers_for_call_with_parsed))


# [ML] сохранение объявлений с внешних площадок
register_kafka_consumer(
    command=cli.command('save-parsed-offers'),
    topic='ml-content-copying.change',
    group_id='external-offers.save-external-offers',
    callback=save_parsed_offers_callback,
    default_max_bulk_size=25,
    message_type=entities.ParsedOfferMessage
)
