import json
from datetime import datetime

import pytz
from cian_core.runtime_settings import runtime_settings

from external_offers.entities.clients import Client, UserSegment
from external_offers.entities.offers import Offer
from external_offers.entities.parsed_offers import ParsedOfferMessage
from external_offers.entities.test_objects import (
    CreateTestClientRequest,
    CreateTestClientResponse,
    CreateTestOfferRequest,
    CreateTestOfferResponse,
    DeleteTestObjectsRequest,
    DeleteTestObjectsResponse,
)
from external_offers.enums.client_status import ClientStatus
from external_offers.enums.offer_status import OfferStatus
from external_offers.helpers.uuid import generate_guid
from external_offers.repositories.postgresql.clients import (
    delete_test_clients,
    get_client_by_avito_user_id,
    save_client,
)
from external_offers.repositories.postgresql.offers import (
    delete_test_offers_for_call,
    save_offer_for_call,
    set_waiting_offers_priority_by_offer_ids,
)
from external_offers.repositories.postgresql.parsed_offers import (
    get_parsed_offer_for_creation_by_id,
    save_test_parsed_offer,
)


def get_attr(obj, attr):
    if isinstance(obj, (CreateTestClientRequest, CreateTestOfferRequest)):
        attr = getattr(obj, attr)
    elif isinstance(obj, dict):
        attr = obj[attr]
    else:
        raise Exception('Invalid request instance')
    return attr


async def create_test_client_public(request: CreateTestClientRequest, user_id: int) -> CreateTestClientResponse:
    DEFAULT_TEST_CLIENT = runtime_settings.DEFAULT_TEST_CLIENT
    if isinstance(DEFAULT_TEST_CLIENT, str):
        DEFAULT_TEST_CLIENT = json.loads(DEFAULT_TEST_CLIENT)
    obj = DEFAULT_TEST_CLIENT if request.use_default else request
    client_id = generate_guid()
    client = Client(
        # dynamic params from request
        avito_user_id=get_attr(obj, 'avito_user_id'),
        client_phones=[get_attr(obj, 'client_phone')],
        client_name=get_attr(obj, 'client_name'),
        cian_user_id=get_attr(obj, 'cian_user_id'),
        client_email=get_attr(obj, 'client_email'),
        segment=UserSegment.from_str(get_attr(obj, 'segment')),
        main_account_chosen=get_attr(obj, 'main_account_chosen'),
        # static params
        is_test=True,
        client_id=client_id,
        status=ClientStatus.waiting,
        operator_user_id=None,
        last_call_id=None,
        calls_count=0,
        next_call=None,
    )
    await save_client(
        client=client
    )
    return CreateTestClientResponse(
        success=True,
        message='Тестовый клиент был успешно создан.',
        client_id=client_id,
    )


async def create_test_offer_public(request: CreateTestOfferRequest, user_id: int) -> CreateTestOfferResponse:
    DEFAULT_TEST_OFFER = runtime_settings.DEFAULT_TEST_OFFER
    if isinstance(DEFAULT_TEST_OFFER, str):
        DEFAULT_TEST_OFFER = json.loads(DEFAULT_TEST_OFFER)
    obj = DEFAULT_TEST_OFFER if request.use_default else request
    # # # parsed_offer
    parsed_offer_message = ParsedOfferMessage(
        id=get_attr(obj, 'parsed_id'),
        source_object_id=get_attr(obj, 'source_object_id'),
        is_calltracking=get_attr(obj, 'is_calltracking'),
        source_user_id=get_attr(obj, 'source_user_id'),
        user_segment=UserSegment.from_str(get_attr(obj, 'user_segment')),
        timestamp=datetime.now(tz=pytz.UTC),
        source_object_model={
            'phones': [get_attr(obj, 'phone')],
            'category': get_attr(obj, 'category'),
            'title': get_attr(obj, 'title'),
            'address': get_attr(obj, 'address'),
            'region': get_attr(obj, 'region'),
            'price': get_attr(obj, 'price'),
            'price_type': get_attr(obj, 'price_type'),
            'contact': get_attr(obj, 'contact'),
            'total_area': get_attr(obj, 'total_area'),
            'floor_number': get_attr(obj, 'floor_number'),
            'floors_count': get_attr(obj, 'floors_count'),
            'rooms_count': get_attr(obj, 'rooms_count'),
            'url': get_attr(obj, 'url'),
            'is_agency': get_attr(obj, 'is_agency'),
            'is_developer': get_attr(obj, 'is_developer'),
            'is_studio': get_attr(obj, 'is_studio'),
            'town': get_attr(obj, 'town'),
            'lat': get_attr(obj, 'lat'),
            'lng': get_attr(obj, 'lng'),
            'living_area': get_attr(obj, 'living_area'),
            'description': get_attr(obj, 'description'),
        },
    )
    await save_test_parsed_offer(parsed_offer=parsed_offer_message)
    parsed_offer = await get_parsed_offer_for_creation_by_id(id=get_attr(obj, 'parsed_id'))
    # # # offer
    client = await get_client_by_avito_user_id(
        avito_user_id=get_attr(obj, 'source_user_id'),
    )
    offer_id = generate_guid()
    offer = Offer(
        # dynamic params from request
        priority=get_attr(obj, 'offer_priority'),
        offer_cian_id=get_attr(obj, 'offer_cian_id'),
        # static params
        is_test=True,
        promocode=None,
        last_call_id=None,
        id=offer_id,
        status=OfferStatus.waiting,
        created_at=datetime.now(tz=pytz.utc),
        started_at=None,
        synced_with_kafka=False,
        client_id=client.client_id,
        synced_at=parsed_offer.timestamp,
        parsed_created_at=parsed_offer.created_at,
        parsed_id=parsed_offer.id,
        category=get_attr(obj, 'category'),
    )
    await save_offer_for_call(offer=offer)
    await set_waiting_offers_priority_by_offer_ids(
        offer_ids=[offer.id],
        priority=get_attr(obj, 'offer_priority')
    )
    return CreateTestOfferResponse(
        success=True,
        message='Тестовое обьявление было успешно создано.',
        offer_id=offer.id,
    )


async def delete_test_objects_public(request: DeleteTestObjectsRequest, user_id: int) -> DeleteTestObjectsResponse:
    await delete_test_clients()
    await delete_test_offers_for_call()
    return DeleteTestObjectsResponse(
        success=True,
        message='Тестовые обьекты были успешно удалены.',
    )
