from typing import List

from cian_core.degradation import DegradationResult, degradation as get_degradation_handler

from external_offers.repositories.moderation_confidence_index import (
    api_call_component_v1_get_operator_calls,
)
from external_offers.repositories.moderation_confidence_index.entities import (
    GetOperatorCallsResponseModel,
    OperatorCallModel,
)


v1_get_operator_calls_degradation_handler = get_degradation_handler(
    func=api_call_component_v1_get_operator_calls,
    default=GetOperatorCallsResponseModel(calls=[]),
    key='api_call_component_v1_get_operator_calls',
)


async def get_operator_calls(operator_id) -> List[OperatorCallModel]:
    request = operator_id
    result: DegradationResult[GetOperatorCallsResponseModel] = await v1_get_operator_calls_degradation_handler()
    return result.value.calls
