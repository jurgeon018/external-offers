# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client announcements`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class V2GetUserActiveAnnouncementsCount:
    user_id: Optional[int] = None
