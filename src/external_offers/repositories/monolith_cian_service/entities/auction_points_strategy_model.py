# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-service`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from datetime import datetime as _datetime


@dataclass
class AuctionPointsStrategyModel:
    """Бонусные деньги."""

    end_date: _datetime
    """Cрок действия бонуса"""
    fee_value: float
    """Величина денежного вознагражения"""
