# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.17.0

"""
from dataclasses import dataclass
from typing import List, Optional

from cian_enum import NoFormat, StrEnum

from .tariff_identificator import TariffIdentificator


class ExcludedServices(StrEnum):
    __value_format__ = NoFormat
    highlight = 'highlight'
    """<a href="http://www.cian.ru/promo/adv/#color" target="_blank">Выделение цветом</a>"""
    premium = 'premium'
    """<a href="http://www.cian.ru/promo/adv/#premium" target="_blank">Премиум-объявление</a>"""
    top3 = 'top3'
    """<a href="http://www.cian.ru/promo/adv/#top3" target="_blank">Топ</a>"""


class Services(StrEnum):
    __value_format__ = NoFormat
    free = 'free'
    """Бесплатное"""
    highlight = 'highlight'
    """<a href="http://www.cian.ru/promo/adv/#color" target="_blank">Выделение цветом</a>"""
    paid = 'paid'
    """Платное"""
    premium = 'premium'
    """<a href="http://www.cian.ru/promo/adv/#premium" target="_blank">Премиум-объявление</a>"""
    top3 = 'top3'
    """<a href="http://www.cian.ru/promo/adv/#top3" target="_blank">Топ</a>"""
    calltracking = 'calltracking'
    """Защита номера"""
    auction = 'auction'
    """Аукцион"""


class Type(StrEnum):
    __value_format__ = NoFormat
    daily_limited = 'dailyLimited'
    """Ограниченная по дням публикация, подневная тарификация"""
    daily_termless = 'dailyTermless'
    """Бессрочная публикация, подневная тарификация"""
    periodical = 'periodical'
    """Тарификация за весь период"""


@dataclass
class PublishTerm:
    """Условия размещения"""

    days: Optional[int] = None
    """Количество дней"""
    dynamic_price: Optional[float] = None
    """Стоимость услуги, которая может меняться пользователем"""
    excluded_services: Optional[List[ExcludedServices]] = None
    """Условия размещения, которые нельзя применять к объявлению"""
    ignore_service_packages: Optional[bool] = None
    """Не использовать пакет размещений при публикации объявления"""
    services: Optional[List[Services]] = None
    """Список размещений"""
    tariff_identificator: Optional[TariffIdentificator] = None
    """Идентификатор записи в тарифной сетке."""
    type: Optional[Type] = None
    """Тип тарификации"""
