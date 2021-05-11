# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-service`

cian-codegen version: 1.12.2

"""
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


class CalculationType(StrEnum):
    __value_format__ = NoFormat
    fixed_amount = 'FixedAmount'
    """Фиксированная сумма"""
    payment_percent = 'PaymentPercent'
    """Процент от платежа"""


@dataclass
class BonusOnPaymentStrategyModel:
    """Бонус на пополнение."""

    calculation_type: CalculationType
    """Способ начисления"""
    fixed_amount: Optional[float] = None
    """Фиксированная сумма"""
    max_amount: Optional[float] = None
    """Максимальный бонус"""
    min_payment: Optional[float] = None
    """Минимальный платёж"""
    payment_percent: Optional[float] = None
    """Процент от платежа"""
    unlimited_usage: Optional[bool] = None
    """Бесконечное число раз"""
    usages_count: Optional[int] = None
    """Сколько раз можно применить"""
