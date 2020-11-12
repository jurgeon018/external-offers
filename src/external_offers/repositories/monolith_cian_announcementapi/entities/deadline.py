# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import Optional

from cian_enum import NoFormat, StrEnum


class Quarter(StrEnum):
    __value_format__ = NoFormat
    first = 'first'
    """Первый"""
    second = 'second'
    """Второй"""
    third = 'third'
    """Третий"""
    fourth = 'fourth'
    """Четвертый"""


@dataclass
class Deadline:
    is_complete: Optional[bool] = None
    """Дом сдан"""
    quarter: Optional[Quarter] = None
    """Квартал"""
    year: Optional[int] = None
    """Срок сдачи"""