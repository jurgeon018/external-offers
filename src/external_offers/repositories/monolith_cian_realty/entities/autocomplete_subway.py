# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-realty`

cian-codegen version: 1.9.0

"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class AutocompleteSubway:
    color: Optional[str] = None
    id: Optional[int] = None
    name: Optional[str] = None
    time_by_car: Optional[int] = None
    time_by_walk: Optional[int] = None
