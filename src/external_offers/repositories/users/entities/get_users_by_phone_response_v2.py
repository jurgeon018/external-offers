# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client users`

cian-codegen version: 1.9.0

"""
from dataclasses import dataclass
from typing import List, Optional

from .user_model_v2 import UserModelV2


@dataclass
class GetUsersByPhoneResponseV2:
    """Пользователи с указанным номером телефона"""

    users: Optional[List[UserModelV2]] = None
    """Пользователи"""
