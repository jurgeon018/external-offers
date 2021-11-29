import logging
import uuid
from datetime import datetime

import pytz
from cian_core.statsd import statsd
from cian_kafka import KafkaProducerError
from simple_settings import settings

from external_offers import pg
from external_offers.entities.kafka import TeamKafkaMessage
from external_offers.queue.kafka import teams_change_producer
from external_offers.repositories.postgresql import iterate_over_teams_sorted


logger = logging.getLogger(__name__)


async def send_teams_to_kafka():
    async with pg.get().transaction():
        async for team in iterate_over_teams_sorted(
            prefetch=settings.TEAMS_FOR_KAFKA_FETCH_LIMIT
        ):
            now = datetime.now(pytz.utc)

            try:
                await teams_change_producer(
                    message=TeamKafkaMessage(
                        team=team,
                        operation_id=str(uuid.uuid1()),
                        date=now
                    ),
                    timeout=settings.DEFAULT_KAFKA_TIMEOUT
                )
            except KafkaProducerError:
                logger.warning('Не удалось отправить событие для команды %s', team.id)
                statsd.incr(
                    stat='send-teams-to-kafka.failed',
                )
            statsd.incr(
                stat='send-teams-to-kafka.success',
            )
