# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client announcements`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass


@dataclass
class GetAnnouncementCountResponse:
    """Ответ на запрос на получение количества объявлений"""

    count: int
    """Количество объявлений"""
