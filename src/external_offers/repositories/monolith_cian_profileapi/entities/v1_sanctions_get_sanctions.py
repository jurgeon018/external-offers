# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-profileapi`

cian-codegen version: 1.14.2

"""
from dataclasses import dataclass
from typing import List


@dataclass
class V1SanctionsGetSanctions:
    user_ids: List[int]
    """Список RealtyUserIds пользователей"""