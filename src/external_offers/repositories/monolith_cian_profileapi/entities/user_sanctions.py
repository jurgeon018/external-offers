# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-profileapi`

cian-codegen version: 1.14.2

"""
from dataclasses import dataclass
from typing import List, Optional

from .user_sanction_item import UserSanctionItem


@dataclass
class UserSanctions:
    sanctions: Optional[List[UserSanctionItem]] = None
    """Список санкций"""
    user_id: Optional[int] = None
    """RealtyId пользователя"""
