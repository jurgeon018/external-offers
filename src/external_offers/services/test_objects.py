from cian_core.runtime_settings import runtime_settings
from external_offers.entities.test_objects import (
    CreateTestClientRequest, CreateTestClientResponse,
    CreateTestOfferRequest, CreateTestOfferResponse,
)

from external_offers.entities.clients import Client, UserSegment
from external_offers.entities.parsed_offers import ParsedOfferMessage
from external_offers.entities.offers import Offer
from external_offers.enums.client_status import ClientStatus
from external_offers.enums.user_segment import UserSegment
from external_offers.enums.offer_status import OfferStatus
from external_offers.helpers.uuid import generate_guid

from external_offers.repositories.postgresql.clients import save_client, get_client_by_avito_user_id
from external_offers.repositories.postgresql.parsed_offers import save_parsed_offer, get_parsed_offer_for_creation_by_id
from external_offers.repositories.postgresql.offers import save_offer_for_call, set_waiting_offers_priority_by_offer_ids


from datetime import datetime
import pytz
import json


def get_attr(obj, attr):
    if isinstance(obj, (CreateTestClientRequest, CreateTestOfferRequest)):
        return getattr(obj, attr)
    elif isinstance(obj, dict):
        return obj[attr]


async def create_test_client_public(request: CreateTestClientRequest, user_id: int) -> CreateTestClientResponse:
    client_id = generate_guid()
    if request.use_default:
        obj = json.loads(runtime_settings.DEFAULT_TEST_CLIENT)
    else:
        obj = request
    avito_user_id = get_attr(obj, 'avito_user_id')
    client_phones = get_attr(obj, 'client_phone')
    client_name = get_attr(obj, 'client_name')
    cian_user_id = get_attr(obj, 'cian_user_id')
    client_email = get_attr(obj, 'client_email')
    segment = get_attr(obj, 'segment')
    main_account_chosen = get_attr(obj, 'main_account_chosen')
    client = Client(
        # dynamic params from request
        avito_user_id = avito_user_id,
        client_phones = [client_phones],
        client_name = client_name,
        cian_user_id = cian_user_id,
        client_email = client_email,
        segment = UserSegment.from_str(segment),
        main_account_chosen = main_account_chosen,
        # static params
        is_test = True,
        client_id = client_id,
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
        message=f'Тестовый клиент был успешно создан.',
        client_id=client_id,
    )



async def create_test_offer_public(request: CreateTestOfferRequest, user_id: int) -> CreateTestOfferResponse:
    if request.use_default:
        obj = runtime_settings.DEFAULT_TEST_OFFER
    else:
        obj = request
    parsed_id = get_attr(obj, 'parsed_id')
    source_object_id = get_attr(obj, 'source_object_id')
    is_calltracking = get_attr(obj, 'is_calltracking')
    source_user_id = get_attr(obj, 'source_user_id')
    user_segment = get_attr(obj, 'user_segment')
    phone = get_attr(obj, 'phone')
    category = get_attr(obj, 'category')
    title = get_attr(obj, 'title')
    address = get_attr(obj, 'address')
    region = get_attr(obj, 'region')
    price = get_attr(obj, 'price')
    price_type = get_attr(obj, 'price_type')
    contact = get_attr(obj, 'contact')
    total_area = get_attr(obj, 'total_area')
    floor_number = get_attr(obj, 'floor_number')
    floors_count = get_attr(obj, 'floors_count')
    rooms_count = get_attr(obj, 'rooms_count')
    url = get_attr(obj, 'url')
    is_agency = get_attr(obj, 'is_agency')
    is_developer = get_attr(obj, 'is_developer')
    is_studio = get_attr(obj, 'is_studio')
    town = get_attr(obj, 'town')
    lat = get_attr(obj, 'lat')
    lng = get_attr(obj, 'lng')
    living_area = get_attr(obj, 'living_area')
    description = get_attr(obj, 'description')
    offer_priority = get_attr(obj, 'offer_priority')
    offer_cian_id = get_attr(obj, 'offer_cian_id')
    # # # parsed_offer
    po_timestamp = datetime.now(tz=pytz.UTC)
    parsed_offer_message = ParsedOfferMessage(
        # static params
        timestamp = po_timestamp,
        # dynamic params from request
        id = parsed_id,
        source_object_id = source_object_id,
        is_calltracking = is_calltracking,
        source_user_id = source_user_id,
        user_segment = UserSegment.from_str(user_segment),
        source_object_model = {
            'phones': [phone],
            'category': category,
            'title': title,
            'address': address,
            'region': region,
            'price': price,
            'price_type': price_type,
            'contact': contact,
            'total_area': total_area,
            'floor_number': floor_number,
            'floors_count': floors_count,
            'rooms_count': rooms_count,
            'url': url,
            'is_agency': is_agency,
            'is_developer': is_developer,
            'is_studio': is_studio,
            'town': town,
            'lat': lat,
            'lng': lng,
            'living_area': living_area,
            'description': description,
        },
    )
    await save_parsed_offer(parsed_offer=parsed_offer_message)
    parsed_offer = await get_parsed_offer_for_creation_by_id(id=parsed_id)
    # # # offer
    client = await get_client_by_avito_user_id(
        avito_user_id=source_user_id,
    )
    offer_id = generate_guid()
    offer = Offer(
        # dynamic params from request
        category=category,
        priority=offer_priority,
        offer_cian_id=offer_cian_id,
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
    )
    await save_offer_for_call(offer=offer)
    await set_waiting_offers_priority_by_offer_ids(
        offer_ids=[offer.id],
        priority=offer_priority
    )
    return CreateTestOfferResponse(
        success=True,
        message=f'Тестовое обьявление было успешно создано.',
        offer_id=offer.id,
    )
