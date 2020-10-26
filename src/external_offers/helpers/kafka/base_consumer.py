import logging
from typing import Any, Callable, Coroutine, List, Type

import click
from cian_kafka import KafkaConsumer, KafkaConsumerMessage
from simple_settings import settings
from tornado.ioloop import IOLoop


logger = logging.getLogger(__name__)


def register_kafka_consumer(
        command: Callable[[Callable[..., Any]], click.core.Command],
        callback: Callable[[List[KafkaConsumerMessage]], Coroutine[Any, Any, None]],
        topic: str,
        consumer_group: str,
        default_bulk_size: int = 20,
        default_bulk_duration: float = 0.5,
        consumer_cls: Type[KafkaConsumer] = KafkaConsumer,
) -> click.core.Command:
    @command
    @click.option(
        '--bulk-duration',
        type=int,
        default=default_bulk_duration,
        show_default=True
    )
    @click.option(
        '--bulk-size',
        type=float,
        default=default_bulk_size,
        show_default=True
    )
    def result_command(bulk_size: int, bulk_duration: float) -> None:
        logger.info('Setup kafka consumer connection with params: %s', settings.KAFKA_CONNECTION)
        consumer = consumer_cls(
            config={
                'bootstrap.servers': settings.KAFKA_CONNECTION['hosts'],
                'group.id': consumer_group,
            },
            topic=topic,
            max_bulk_size=bulk_size,
            poll_timeout=bulk_duration,
            callback=callback,
        )
        IOLoop.current().run_sync(consumer.start)

    return result_command
