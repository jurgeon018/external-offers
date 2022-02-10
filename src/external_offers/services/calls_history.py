from datetime import datetime
from typing import List, Optional

from cian_core.degradation import DegradationResult, degradation as get_degradation_handler

from external_offers.repositories.moderation_confidence_index import (
    api_call_component_v1_get_operator_calls,
)
from external_offers.repositories.moderation_confidence_index.entities import (
    GetOperatorCallsResponseModel,
    OperatorCallModel, GetOperatorCallsFilter,
)


v1_get_operator_calls_degradation_handler = get_degradation_handler(
    func=api_call_component_v1_get_operator_calls,
    default=GetOperatorCallsResponseModel(calls=[]),
    key='api_call_component_v1_get_operator_calls',
)


async def get_operator_calls(
        *,
        operator_id: int,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
        phone_from: Optional[str] = None,
        phone_to: Optional[str] = None,
        task_key: Optional[str] = None,
        team: Optional[str] = None,
        time_from: Optional[datetime] = None,
        time_to: Optional[datetime] = None,
) -> List[OperatorCallModel]:
    request = GetOperatorCallsFilter(
        operator_id=operator_id,
        page=page,
        page_size=page_size,
        phone_from=phone_from,
        phone_to=phone_to,
        task_key=task_key,
        team=team,
        time_from=time_from,
        time_to=time_to,
    )
    result: DegradationResult[GetOperatorCallsResponseModel] = await v1_get_operator_calls_degradation_handler(request)
    return result.value.calls
