# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.9.0

"""
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


class Type(StrEnum):
    __value_format__ = NoFormat
    cargo = 'cargo'
    """Грузовой"""
    escalator = 'escalator'
    """Эскалатор"""
    lift = 'lift'
    """Лифт"""
    passenger = 'passenger'
    """Пассажирский"""
    telpher = 'telpher'
    """Тельфер"""
    travelator = 'travelator'
    """Траволатор"""


@dataclass
class LiftType:
    """Лифты"""

    additional_type: Optional[str] = None
    """Дополнительный тип"""
    count: Optional[int] = None
    """Количество"""
    load_capacity: Optional[float] = None
    """Грузоподъёмность"""
    type: Optional[Type] = None
    """Тип лифта"""
