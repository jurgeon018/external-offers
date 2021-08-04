import os

from typing import List, Type

from simple_settings import settings

from cian_core.rabbitmq.consumer import Exchange, QueueBinding
from cian_enum import StrEnum


def get_bindings(exchange: str, prefix: str, enum: Type[StrEnum]) -> List[QueueBinding]:
    result: List[QueueBinding] = []
    values: List[StrEnum] = list(enum)
    for item in values:
        result.append(
            QueueBinding(
                exchange=Exchange(exchange),
                routing_key='{}.{}'.format(prefix, item.value),
            )
        )
    return result


def get_modified_queue_name(queue_name: str) -> str:
    return f'{settings.APPLICATION_NAME}.{queue_name}{_get_branch_suffix()}'


def _get_branch_suffix() -> str:
    branch_suffix = os.getenv('BRANCH_NAME', '')
    if branch_suffix and 'master' not in branch_suffix:
        return '.' + branch_suffix
    return ''
