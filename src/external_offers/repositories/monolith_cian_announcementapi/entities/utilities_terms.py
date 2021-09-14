# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.17.0

"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class UtilitiesTerms:
    """Коммунальные платежи"""

    flow_meters_not_included_in_price: Optional[bool] = None
    """Счетчики оплачиваются отдельно"""
    included_in_price: Optional[bool] = None
    """Включены в стоимость"""
    price: Optional[float] = None
    """Сумма платежей"""
