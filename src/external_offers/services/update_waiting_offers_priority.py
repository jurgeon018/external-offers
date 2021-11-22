

from external_offers.entities.response import BasicResponse
from external_offers.entities.update_waiting_offers_priority import PrioritizeWaitingOffersRequest
from external_offers.repositories.postgresql.teams import get_team_by_id
from external_offers.services.offers_creator import prioritize_waiting_offers


async def prioritize_waiting_offers_public(
    request: PrioritizeWaitingOffersRequest,
    user_id: int
) -> BasicResponse:
    team_id = int(request.team_id)
    team = await get_team_by_id(team_id)
    await prioritize_waiting_offers(team=team)
    return BasicResponse(
        success=True,
        message=f'Приоритеты для команды {team_id} были успешно изменены',
    )
