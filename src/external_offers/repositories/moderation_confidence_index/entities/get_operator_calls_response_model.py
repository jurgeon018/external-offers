# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client moderation-confidence-index`

cian-codegen version: 2.0.0

"""
from dataclasses import dataclass
from typing import Optional

from .operator_call_model import OperatorCallModel


@dataclass
class GetOperatorCallsResponseModel:
    """Модель ответа получить звонки"""

    calls: Optional[list[OperatorCallModel]] = None
    """Звонки"""
    total: Optional[int] = None
    """Сколько всего найдено записей согласно фильтру"""
