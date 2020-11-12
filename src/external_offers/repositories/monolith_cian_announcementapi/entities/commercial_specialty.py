# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-announcementapi`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class CommercialSpecialty:
    """Назначение"""

    additional_types: Optional[List[str]] = None
    """Дополнительные виды"""
    types: Optional[List[str]] = None
    """Возможное назначение (<a href="https://www.cian.ru/xml_import/commercial-possible-appointments.xml" target="_blank">ссылка на справочник</a>)"""