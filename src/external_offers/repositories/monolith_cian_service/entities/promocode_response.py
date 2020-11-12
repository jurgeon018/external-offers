# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-service`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class PromocodeResponse:
    """Промокод."""

    promocode: str
    """Промокод."""
    cian_user_id: Optional[int] = None
    """Cian id пользователя, к которому привязан промокод."""
    user_id: Optional[int] = None
    """К какому пользователю привязан. Не заполняется если промокод доступен любому пользователю."""
