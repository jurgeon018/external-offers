from external_offers.entities.create_test_client import CreateTestClientRequest, CreateTestClientResponse
from external_offers.entities.create_test_offer import CreateTestOfferRequest, CreateTestOfferResponse
from external_offers.entities.clients import Client
from external_offers.entities.parsed_offers import ParsedOfferMessage
from external_offers.entities.offers import Offer

from external_offers.repositories.postgresql.clients import save_client, get_client_by_avito_user_id
from external_offers.repositories.postgresql.parsed_offers import save_parsed_offer, get_parsed_offer_for_creation_by_id
from external_offers.repositories.postgresql.offers import save_offer_for_call, set_waiting_offers_priority_by_offer_ids

from external_offers.enums.offer_status import OfferStatus
from external_offers.enums.client_status import ClientStatus
from external_offers.helpers.uuid import generate_guid

from datetime import datetime
import pytz


async def create_test_client_public(request: CreateTestClientRequest, user_id: int) -> CreateTestClientResponse:
    client_id = generate_guid()
    client = Client(
        # dynamic params
        avito_user_id = request.avito_user_id,
        client_phones = request.client_phones,
        client_name = request.client_name,
        cian_user_id = request.cian_user_id,
        client_email = request.client_email,
        segment = request.segment,
        main_account_chosen = request.main_account_chosen,
        # static params
        client_id = client_id,
        is_test = True,
        status = ClientStatus.waiting,
        operator_user_id = None,
        last_call_id = None,
        calls_count = 0,
        next_call = None,
    )
    await save_client(
        client=client
    )
    return CreateTestClientResponse(
        success=True,
        message=f'Тестовый клиент был успешно создан. id: {client_id}'
    )


async def create_test_offer_public(request: CreateTestOfferRequest, user_id: int) -> CreateTestOfferResponse:
    client = await get_client_by_avito_user_id(
        avito_user_id=request.source_user_id,
    )
    # parsed_offer
    po_timestamp = datetime.now(tz=pytz.UTC)
    parsed_offer_message = ParsedOfferMessage(
        # dynamic params
        id = request.parsed_id,
        source_object_id = request.source_object_id,
        source_object_model = request.source_object_model,
        is_calltracking = request.is_calltracking,
        source_user_id = request.source_user_id,
        user_segment = request.source_object_model['user_segment'],
        # static params
        timestamp = po_timestamp,
    )
    save_parsed_offer(parsed_offer=parsed_offer_message)
    parsed_offer = await get_parsed_offer_for_creation_by_id(id=request.id)
    # offer
    offer_id = generate_guid()
    offer = Offer(
        # dynamic params
        category=request.category,
        priority=request.offer_priority,
        offer_cian_id=request.offer_cian_id,
        # static params
        promocode='...',
        last_call_id=None,
        is_test=True,
        id=offer_id,
        status=OfferStatus.waiting,
        created_at=datetime.now(tz=pytz.utc),
        started_at=None,
        synced_with_kafka=False,
        client_id=client.client_id,
        synced_at=parsed_offer.timestamp,
        parsed_created_at=parsed_offer.created_at,
        parsed_id=parsed_offer.id,
    )
    save_offer_for_call(offer=offer)
    # await set_waiting_offers_priority_by_offer_ids(
    #     offer_ids=[offer.id],
    #     priority=request.offer_priority
    # )

    return CreateTestOfferResponse(
        success=True,
        message=f'Обьявление было успешно создано. id: {offer.id}'
    )
