from typing import List, NoReturn

import backoff
from cian_core.degradation import DegradationResult, get_degradation_handler

from external_offers.repositories.announcements import public_v1_get_possible_appointments
from external_offers.repositories.announcements.entities import (
    GetPossibleAppointmentItem,
    GetPossibleAppointmentsResponse,
)


public_v1_get_possible_appointments_with_degradation = get_degradation_handler(
    func=public_v1_get_possible_appointments,
    default=GetPossibleAppointmentsResponse(items=[]),
    key='public_v1_get_possible_appointments',
)

def public_v1_get_possible_appointments_retry_predicate(
    degradation_result: DegradationResult[GetPossibleAppointmentsResponse]
) -> bool:
    return degradation_result.degraded


v1_get_possible_appointments_with_retries = backoff.on_predicate(
    backoff.expo,
    predicate=public_v1_get_possible_appointments_retry_predicate,
    max_tries=3,
    on_giveup=None,
)(public_v1_get_possible_appointments_with_degradation)


async def get_possible_appointments() -> List[GetPossibleAppointmentItem]:
    result: DegradationResult[GetPossibleAppointmentsResponse] = await v1_get_possible_appointments_with_retries()
    return result.value.items
