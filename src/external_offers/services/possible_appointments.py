from typing import List

from cian_core.degradation import DegradationResult, get_degradation_handler

from external_offers.repositories.announcements import public_v1_get_possible_appointments
from external_offers.repositories.announcements.entities import (
    GetPossibleAppointmentItem,
    GetPossibleAppointmentsResponse,
)


v1_get_possible_appointments_with_degradation = get_degradation_handler(
    func=public_v1_get_possible_appointments,
    default=GetPossibleAppointmentsResponse(items=[]),
    key='public_v1_get_possible_appointments',
)


async def get_possible_appointments() -> List[GetPossibleAppointmentItem]:
    result: DegradationResult[GetPossibleAppointmentsResponse] = await v1_get_possible_appointments_with_degradation()
    return result.value.items
