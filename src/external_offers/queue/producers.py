from datetime import datetime
from typing import Optional

import pytz
from cian_core.context import get_or_create_operation_id
from cian_core.rabbitmq.decorators import mq_producer_v2
from cian_core.rabbitmq import RabbitMQEntityProducer

from external_offers.entities.operators import EnrichedOperator
from external_offers.queue.entities import OperatorMessage
from external_offers.queue.routing_keys import OperatorV1RoutingKey


def build_operator_message(operator: Optional[EnrichedOperator]) -> OperatorMessage:
    return OperatorMessage(
        operator=operator,
        operation_id=get_or_create_operation_id(),
        date=datetime.now(tz=pytz.UTC),
    )


operator_producer = RabbitMQEntityProducer(
    OperatorMessage,
    OperatorV1RoutingKey.updated.value,
)
