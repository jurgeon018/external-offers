from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


@dataclass
class ReasonOfDeclineEnum(StrEnum):
    __value_format__ = NoFormat

    not_effective = 'not_effective'
    """Циан не эффективен"""
    expensive = 'expensive'
    """Дорого"""
    dont_like_support = 'dont_like_support'
    """Не нравится поддержка Циан"""
    difficult_service = 'difficult_service'
    """Сложный сервис"""
    not_a_publisher = 'not_a_publisher'
    """Не я занимаюсь размещением"""
    dont_engage_in_real_estate = 'dont_engage_in_real_estate'
    """Не занимается недвижимостью"""
    only_residential_property = 'only_residential_property'
    """Только жилая"""
    no_offers_and_wont_be = 'no_offers_and_wont_be'
    """Нет объектов и не будет"""
    no_offers_but_will_be = 'no_offers_but_will_be'
    """Нет объектов, но будут"""
    decline_conversation = 'decline_conversation'
    """Сброс в отказ от разговора"""
    not_interested = 'not_interested'
    """Не интересно"""
    dont_trust = 'dont_trust'
    """Не доверяю"""
    have_no_time = 'have_no_time'
    """Нет времени"""
    frequent_calls = 'frequent_calls'
    """Частые звонки"""
    other = 'other'
    """Иное"""


@dataclass
class UpdateClientReasonOfDeclineRequest:
    client_id: str
    """Идентификатор клиента"""
    reasonOfDecline: Optional[ReasonOfDeclineEnum] = None
    """Причина отказа"""


@dataclass
class UpdateClientReasonOfDeclineResponse:
    success: bool
    """Статус операции"""
    message: str
    """Текст ответа"""
