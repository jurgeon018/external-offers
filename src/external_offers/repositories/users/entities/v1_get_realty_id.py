# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client users`

cian-codegen version: 1.17.0

"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class V1GetRealtyId:
    cian_user_id: Optional[int] = None
