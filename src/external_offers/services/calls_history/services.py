from cian_core.degradation import DegradationResult, degradation as get_degradation_handler

from external_offers.repositories.moderation_confidence_index import api_call_component_v1_get_operator_calls
from external_offers.repositories.moderation_confidence_index.entities import (
    GetOperatorCallsFilter,
    GetOperatorCallsResponseModel,
    OperatorCallModel,
)


v1_get_operator_calls_degradation_handler = get_degradation_handler(
    func=api_call_component_v1_get_operator_calls,
    default=GetOperatorCallsResponseModel(calls=[]),
    key='api_call_component_v1_get_operator_calls',
)


async def get_operator_calls(request: GetOperatorCallsFilter) -> list[OperatorCallModel]:
    result: DegradationResult[GetOperatorCallsResponseModel] = await v1_get_operator_calls_degradation_handler(request)
    return result.value.calls or []
