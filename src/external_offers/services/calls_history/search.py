from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from marshmallow import Schema, fields

from external_offers.repositories.moderation_confidence_index.entities import (
    GetOperatorCallsFilter,
    GetOperatorCallsResponseModel,
)
from external_offers.services.calls_history.services import get_operator_calls


class CallHistoryFilterSchema(Schema):
    operator_id = fields.Int()
    time_from = fields.DateTime(format='%Y-%m-%dT%H:%M')
    time_to = fields.DateTime(format='%Y-%m-%dT%H:%M')
    duration_min = fields.Int()
    duration_max = fields.Int()
    page = fields.Int()


@dataclass
class CallsHistorySearch:
    operator_id: int
    """Идентификатор оператора"""
    page: int = 1
    """Номер страницы"""
    page_size: int = 100
    """Размер страницы"""
    phone_from: Optional[str] = None
    """С какого телефона"""
    phone_to: Optional[str] = None
    """На какой телефон"""
    task_key: Optional[str] = None
    """Ключ таски"""
    team: Optional[str] = None
    """Команда"""
    time_from: Optional[datetime] = None
    """Время с"""
    time_to: Optional[datetime] = None
    """Время по"""
    duration_min: Optional[int] = None
    """Минимальная продолжительность разговора"""
    duration_max: Optional[int] = None
    """Максимальная продолжительность разговора"""
    dt_lower_border: Optional[datetime] = None
    """Дата хантинга от"""
    dt_upper_border: Optional[datetime] = None
    """Дата хантинга до"""

    @classmethod
    def from_search_params(cls, data: dict, operator_id: int) -> 'CallsHistorySearch':
        schema = CallHistoryFilterSchema()
        result = schema.load(data).data
        if 'operator_id' not in result:
            result.update({'operator_id': operator_id})
        search = cls(**result)
        return search

    async def execute(self) -> GetOperatorCallsResponseModel:
        request = GetOperatorCallsFilter(
            operator_id=self.operator_id,
            page=self.page,
            page_size=self.page_size,
            phone_from=self.phone_from,
            phone_to=self.phone_to,
            task_key=self.task_key,
            team=self.team,
            time_from=self.time_from,
            time_to=self.time_to,
            duration_max=self.duration_max,
            duration_min=self.duration_min,
        )
        calls = await get_operator_calls(request)
        return calls
