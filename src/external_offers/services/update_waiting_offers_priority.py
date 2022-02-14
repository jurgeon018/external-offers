import asyncio

from external_offers.entities.response import BasicResponse
from external_offers.entities.update_waiting_offers_priority import PrioritizeWaitingOffersRequest
from external_offers.repositories.postgresql.teams import get_team_by_id
from external_offers.services.offers_creator import prioritize_waiting_offers, sync_and_create_offers


async def prioritize_waiting_offers_public(
    request: PrioritizeWaitingOffersRequest,
    user_id: int
) -> BasicResponse:
    is_test = request.is_test
    team_id = request.team_id
    if team_id:
        team = await get_team_by_id(int(team_id))
        message = f'Проставление приоритетов для команды {team_id} было запущено'
    else:
        team = None
        message = f'Проставление приоритетов было запущено'
    asyncio.create_task(prioritize_waiting_offers(teams=[team], is_test=is_test))
    return BasicResponse(
        success=True,
        message=message,
    )


async def create_test_offers_for_call(user_id: int):
    asyncio.create_task(sync_and_create_offers(is_test=True))
    message = 'Синхронизация таблиц offers_for_call и clients на основе parsed_offer была запущена'
    return BasicResponse(
        success=True,
        message=message,
    )
