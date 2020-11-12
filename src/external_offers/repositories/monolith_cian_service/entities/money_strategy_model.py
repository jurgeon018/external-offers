# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-service`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from datetime import datetime as _datetime
from typing import Optional


@dataclass
class MoneyStrategyModel:
    """Бонусные деньги."""

    comment: Optional[str] = None
    """Произвольный комментарий, который будет записан в лог операций после активации промокода."""
    end_date: Optional[_datetime] = None
    """Cрок действия бонуса"""
    fee_value: Optional[float] = None
    """Величина денежного вознагражения"""