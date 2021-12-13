from typing import List

from cian_core.degradation import DegradationResult, degradation as get_degradation_handler

from external_offers.repositories.monolith_cian_announcementapi import (
    announcement_references_commercial_get_possible_appointments,
)
from external_offers.repositories.monolith_cian_announcementapi.entities import CommercialPossibleAppointmentModel


get_possible_appointments_with_degradation = get_degradation_handler(
    func=announcement_references_commercial_get_possible_appointments,
    default=[],
    key='announcement_references_commercial_get_possible_appointments',
)


async def get_possible_appointments() -> List[CommercialPossibleAppointmentModel]:
    result: DegradationResult[List[CommercialPossibleAppointmentModel]] = await get_possible_appointments_with_degradation()
    return result.value
