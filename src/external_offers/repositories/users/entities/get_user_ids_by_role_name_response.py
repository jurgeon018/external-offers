# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client users`

cian-codegen version: 1.16.3

"""
from dataclasses import dataclass
from typing import List


@dataclass
class GetUserIdsByRoleNameResponse:
    """Ответ на получение id пользователей, у которых есть переданная роль"""
    user_ids: List[int]
    """Id пользователей"""
