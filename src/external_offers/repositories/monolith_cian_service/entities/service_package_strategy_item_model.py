# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-service`

cian-codegen version: 1.12.2

"""
from dataclasses import dataclass
from typing import List, Optional

from cian_enum import NoFormat, StrEnum


class DurationInDays(StrEnum):
    __value_format__ = NoFormat
    seven = 'seven'
    """7 дней."""
    fourteen = 'fourteen'
    """14 дней."""
    thirty = 'thirty'
    """30 дней."""
    sixty = 'sixty'
    """60 дней."""
    ninety = 'ninety'
    """90 дней."""
    one_hundred_eighty = 'oneHundredEighty'
    """180 дней."""
    three_hundred_sixty = 'threeHundredSixty'
    """360 дней."""


class ObjectTypeId(StrEnum):
    __value_format__ = NoFormat
    any = 'any'
    """Любой."""
    flat = 'flat'
    """Городская."""
    commercial = 'commercial'
    """Коммерческая."""
    suburbian = 'suburbian'
    """Загородная."""


class OperationTypes(StrEnum):
    __value_format__ = NoFormat
    sale = 'sale'
    """Продажа."""
    rent = 'rent'
    """Аренда."""


@dataclass
class ServicePackageStrategyItemModel:
    duration_in_days: DurationInDays
    """Длительность в днях (с фиксированными значениями). Впоследствие можно отказаться от этого поля в пользу {Web.Admin.App.PromoCode.Models.ServicePackageStrategyItemModel.DurationDays}"""
    object_type_id: ObjectTypeId
    """Тип недвижимости"""
    operation_types: List[OperationTypes]
    'Типы сделки\r\n(аренда, продажа)'
    polygon_ids: List[int]
    """Регионы."""
    auction_points: Optional[float] = None
    """Количество баллов на аукцион"""
    debit_count: Optional[int] = None
    """Количество платных слотов."""
    highlight_count: Optional[int] = None
    """Количество слотов на выделение цветом."""
    premium_count: Optional[int] = None
    """Количество премиум слотов."""
    premium_highlight_count: Optional[int] = None
    """Количество слотов Премиум + Выделение цветом."""
    top3_count: Optional[int] = None
    """Количество Топ слотов."""
