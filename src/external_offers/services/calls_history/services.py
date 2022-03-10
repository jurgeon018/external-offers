from cian_core.degradation import DegradationResult, degradation as get_degradation_handler

from external_offers.repositories.moderation_confidence_index import (
    api_call_component_v1_get_operator_calls,
    api_call_component_v1_operator_calls_create_csv_report,
    api_call_component_v1_operator_calls_download_csv_reportcsv,
    api_call_component_v1_operator_calls_get_csv_report_status,
)
from external_offers.repositories.moderation_confidence_index.entities import (
    ApiCallComponentV1OperatorCallsDownloadCsvReportcsv,
    GenerateCsvResponseModel,
    GetCsvReportStatusRequestModel,
    GetCsvReportStatusResponseModel,
    GetOperatorCallsFilter,
    GetOperatorCallsResponseModel,
)


v1_get_operator_calls_degradation_handler = get_degradation_handler(
    func=api_call_component_v1_get_operator_calls,
    default=GetOperatorCallsResponseModel(calls=[], total=0),
    key='api_call_component_v1_get_operator_calls',
)


async def get_operator_calls(request: GetOperatorCallsFilter) -> GetOperatorCallsResponseModel:
    result: DegradationResult[GetOperatorCallsResponseModel] = await v1_get_operator_calls_degradation_handler(request)
    return result.value


async def create_csv_report(request: GetOperatorCallsFilter, user_id: int) -> GenerateCsvResponseModel:
    resp = await api_call_component_v1_operator_calls_create_csv_report(request)
    return resp


async def get_csv_report_status(
        request: GetCsvReportStatusRequestModel,
        user_id: int,
) -> GetCsvReportStatusResponseModel:
    resp = await api_call_component_v1_operator_calls_get_csv_report_status(request)
    return resp


async def download_csv(
        request: ApiCallComponentV1OperatorCallsDownloadCsvReportcsv,
        user_id: int,
):
    resp = await api_call_component_v1_operator_calls_download_csv_reportcsv(request)
    resp.content = resp.content.decode()  # type: ignore # В resp.content приходят байты, но в json должны быть строка
    return resp
