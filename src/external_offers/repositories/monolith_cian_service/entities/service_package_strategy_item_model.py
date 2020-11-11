# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-service`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import List, Optional

from cian_enum import NoFormat, StrEnum

from .select_list_item import SelectListItem


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
    """Жилая."""
    commercial = 'commercial'
    """Коммерческая."""
    suburbian = 'suburbian'
    """Загородная."""


class OperationTypeId(StrEnum):
    __value_format__ = NoFormat
    sale = 'sale'
    """Продажа."""
    rent = 'rent'
    """Аренда."""


class OperationTypes(StrEnum):
    __value_format__ = NoFormat
    sale = 'sale'
    """Продажа."""
    rent = 'rent'
    """Аренда."""


@dataclass
class ServicePackageStrategyItemModel:
    duration_in_days: DurationInDays
    object_type_id: ObjectTypeId
    """Тип недвижимости"""
    polygon_ids: List[int]
    """Регионы."""
    auction_points: Optional[float] = None
    """Количество баллов на аукцион"""
    debit_count: Optional[int] = None
    """Количество платных слотов."""
    highlight_count: Optional[int] = None
    """Количество слотов на выделение цветом."""
    operation_type_id: Optional[OperationTypeId] = None
    """Тип сделки."""
    operation_type_source_list: Optional[List[SelectListItem]] = None
    """Все возможные типы сделки"""
    operation_types: Optional[List[OperationTypes]] = None
    'Типы сделки\r\n(аренда, продажа)'
    premium_count: Optional[int] = None
    """Количество премиум слотов."""
    premium_highlight_count: Optional[int] = None
    """Количество слотов Премиум + Выделение цветом."""
    top3_count: Optional[int] = None
    """Количество Топ слотов."""
