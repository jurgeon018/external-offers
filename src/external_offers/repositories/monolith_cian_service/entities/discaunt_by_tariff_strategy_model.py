# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-service`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class DiscauntByTariffStrategyModel:
    """Скидка на активацию тарифа."""

    new_min_activation_amount: float
    """Необходимая сумма"""
    package_id: Optional[int] = None
    """Ключ пакета который будет применен пользователю"""