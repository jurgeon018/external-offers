# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


class Currency(StrEnum):
    __value_format__ = NoFormat
    eur = 'eur'
    """Евро"""
    rur = 'rur'
    """Рубль"""
    usd = 'usd'
    """Доллар"""


class PaymentType(StrEnum):
    __value_format__ = NoFormat
    percent = 'percent'
    """Процент"""
    fixed = 'fixed'
    """Фиксированный"""


@dataclass
class AgentBonus:
    """Бонус агенту."""

    currency: Optional[Currency] = None
    """Валюта. Указывается при фиксированном типе оплаты"""
    payment_type: Optional[PaymentType] = None
    """Тип оплаты"""
    value: Optional[float] = None
    """Значение"""
