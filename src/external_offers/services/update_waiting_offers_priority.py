import asyncio

from external_offers.entities.response import BasicResponse
from external_offers.entities.update_waiting_offers_priority import PrioritizeWaitingOffersRequest
from external_offers.repositories.postgresql.teams import get_team_by_id
from external_offers.services.offers_creator import prioritize_waiting_offers


async def prioritize_waiting_offers_public(
    request: PrioritizeWaitingOffersRequest,
    user_id: int
) -> BasicResponse:
    team_id = int(request.team_id)
    is_test = request.is_test
    team = await get_team_by_id(team_id)
    asyncio.create_task(prioritize_waiting_offers(team=team, is_test=is_test))
    return BasicResponse(
        success=True,
        message=f'Проставление приоритетов для команды {team_id} было запущено',
    )
