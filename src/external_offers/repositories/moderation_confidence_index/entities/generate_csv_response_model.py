# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client moderation-confidence-index`

cian-codegen version: 2.1.0

"""
from dataclasses import dataclass
from typing import Optional
from uuid import UUID


@dataclass
class GenerateCsvResponseModel:
    """Ответ на запрос создать csv-отчёт"""

    report_id: Optional[UUID] = None
    """Идентификатор отчёта"""
