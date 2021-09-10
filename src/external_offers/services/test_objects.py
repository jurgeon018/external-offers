import json
from datetime import datetime
from typing import Optional, Union

import pytz
from asyncpg.exceptions._base import PostgresError
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
    UpdateTestObjectsPublicationStatusRequest,
    UpdateTestObjectsPublicationStatusResponse,
)
from external_offers.enums.client_status import ClientStatus
from external_offers.enums.offer_status import OfferStatus
from external_offers.helpers.uuid import generate_guid
from external_offers.repositories.postgresql.clients import (
    delete_test_clients,
    get_client_by_avito_user_id,
    get_client_by_client_id,
    save_client,
)
from external_offers.repositories.postgresql.offers import (
    delete_test_offers_for_call,
    get_offer_is_test_by_offer_cian_id,
    get_offer_row_version_by_offer_cian_id,
    save_offer_for_call,
    set_waiting_offers_priority_by_offer_ids,
)
from external_offers.repositories.postgresql.parsed_offers import (
    delete_test_parsed_offers,
    exists_parsed_offer_by_source_object_id,
    get_parsed_offer_for_creation_by_id,
    save_test_parsed_offer,
)
from external_offers.services.announcement import update_publication_status


async def get_default_test_offer():
    return runtime_settings.DEFAULT_TEST_OFFER


async def get_default_test_client():
    return runtime_settings.DEFAULT_TEST_CLIENT


def get_attr(
    obj: Union[dict, CreateTestClientRequest, CreateTestOfferRequest],
    attr: str,
) -> Optional[Union[str, int, bool, datetime]]:
    if isinstance(obj, (CreateTestClientRequest, CreateTestOfferRequest)):
        attr = getattr(obj, attr)
    elif isinstance(obj, dict):
        attr = obj[attr]
    else:
        raise Exception('Invalid request instance')
    return attr


async def create_test_client_public(request: CreateTestClientRequest, user_id: int) -> CreateTestClientResponse:
    """
    Создать тестового клиента.
    """
    source_user_id = request.source_user_id
    client = await get_client_by_avito_user_id(avito_user_id=source_user_id)
    if client:
        return CreateTestClientResponse(
            success=True,
            message=f'Клиент с source_user_id {source_user_id} уже существует.',
            client_id=client.client_id,
        )

    DEFAULT_TEST_CLIENT = await get_default_test_client()
    if isinstance(DEFAULT_TEST_CLIENT, str):
        try:
            DEFAULT_TEST_CLIENT = json.loads(DEFAULT_TEST_CLIENT)
        except json.decoder.JSONDecodeError as e:
            error_message = (
                f'Невалидное значение в переменной DEFAULT_TEST_CLIENT. {e}\n'
                f'DEFAULT_TEST_CLIENT={DEFAULT_TEST_CLIENT}'
            )
            return CreateTestClientResponse(
                success=False,
                message=error_message,
            )
    obj = DEFAULT_TEST_CLIENT if request.use_default else request
    client_id = generate_guid()
    client = Client(
        # dynamic params from request
        avito_user_id=source_user_id,
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
    try:
        await save_client(
            client=client
        )
    except PostgresError as e:
        return CreateTestClientResponse(
            success=False,
            message=f'Не удалось создать клиента из-за ошибки: {e}'
        )
    return CreateTestClientResponse(
        success=True,
        message='Тестовый клиент был успешно создан.',
        client_id=client_id,
    )


async def create_test_offer_public(request: CreateTestOfferRequest, user_id: int) -> CreateTestOfferResponse:
    """
    Создать тестовое обьявление по clientId либо sourceUserId.
    """
    if request.source_user_id:
        source_user_id = request.source_user_id
        client = await get_client_by_avito_user_id(avito_user_id=source_user_id)
        if not client:
            return CreateTestOfferResponse(
                success=False,
                message=f'Клиент с sourceUserId {source_user_id} не существует. Сначала создайте клиента.',
            )
    elif request.client_id:
        client_id = request.client_id
        client = await get_client_by_client_id(client_id=client_id)
        if not client:
            return CreateTestOfferResponse(
                success=False,
                message=f'Клиент с clientId {client_id} не существует. Сначала создайте клиента.',
            )
    else:
        return CreateTestOfferResponse(
            success=False,
            message='Отправьте clientId либо sourceUserId.',
        )
    source_user_id = client.avito_user_id
    source_object_id = request.source_object_id
    exists = await exists_parsed_offer_by_source_object_id(source_object_id=source_object_id)
    if exists:
        return CreateTestOfferResponse(
            success=False,
            message=f'Обьявление с source_object_id {source_object_id} уже существует.',
        )

    DEFAULT_TEST_OFFER = await get_default_test_offer()
    if isinstance(DEFAULT_TEST_OFFER, str):
        try:
            DEFAULT_TEST_OFFER = json.loads(DEFAULT_TEST_OFFER)
        except json.decoder.JSONDecodeError as e:
            error_message = (
                f'Невалидное значение в переменной DEFAULT_TEST_OFFER. {e}\n'
                f'DEFAULT_TEST_OFFER={DEFAULT_TEST_OFFER}'
            )
            return CreateTestOfferResponse(
                success=False,
                message=error_message,
            )
    obj = DEFAULT_TEST_OFFER if request.use_default else request
    # # # parsed_offer
    parsed_offer_message = ParsedOfferMessage(
        source_user_id=source_user_id,
        source_object_id=source_object_id,
        id=get_attr(obj, 'parsed_id'),
        is_calltracking=get_attr(obj, 'is_calltracking'),
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
            'lat': float(get_attr(obj, 'lat')),
            'lng': float(get_attr(obj, 'lng')),
            'living_area': get_attr(obj, 'living_area'),
            'description': get_attr(obj, 'description'),
        },
    )
    try:
        await save_test_parsed_offer(parsed_offer=parsed_offer_message)
    except PostgresError as e:
        error_message = f'Не удалось создать спаршеное обьявление из-за ошибки: {e}'
        return CreateTestOfferResponse(
            success=False,
            message=error_message,
        )
    parsed_offer = await get_parsed_offer_for_creation_by_id(id=get_attr(obj, 'parsed_id'))
    # # # offer
    offer_id = generate_guid()
    if client.status == ClientStatus.waiting:
        offer_status = OfferStatus.waiting
    else:
        offer_status = OfferStatus.in_progress
    offer = Offer(
        # dynamic params from request
        priority=get_attr(obj, 'offer_priority'),
        offer_cian_id=get_attr(obj, 'offer_cian_id'),
        # static params
        is_test=True,
        promocode=None,
        last_call_id=None,
        id=offer_id,
        client_id=client.client_id,
        status=offer_status,
        created_at=datetime.now(tz=pytz.utc),
        started_at=None,
        synced_with_kafka=False,
        synced_at=parsed_offer.timestamp,
        parsed_created_at=parsed_offer.created_at,
        parsed_id=parsed_offer.id,
        category=get_attr(obj, 'category'),
    )
    try:
        await save_offer_for_call(offer=offer)
    except PostgresError as e:
        error_message = f'Не удалось создать задание из-за ошибки: {e}'
        return CreateTestOfferResponse(
            success=False,
            message=error_message,
        )
    await set_waiting_offers_priority_by_offer_ids(
        offer_ids=[offer.id],
        priority=get_attr(obj, 'offer_priority')
    )
    return CreateTestOfferResponse(
        success=True,
        message='Тестовое обьявление было успешно создано.',
        offer_id=offer_id,
    )


async def delete_test_objects_public(request: DeleteTestObjectsRequest, user_id: int) -> DeleteTestObjectsResponse:
    """
    Удалить все тестовые обьекты(клиентов, задания, спаршеные обьявления).
    """
    await delete_test_clients()
    await delete_test_offers_for_call()
    await delete_test_parsed_offers()
    return DeleteTestObjectsResponse(
        success=True,
        message='Тестовые обьекты были успешно удалены.',
    )


async def update_test_objects_publication_status_public(request: UpdateTestObjectsPublicationStatusRequest, user_id: int) -> UpdateTestObjectsPublicationStatusResponse:
    row_version = request.row_version
    offer_cian_id = request.offer_cian_id
    publication_status = request.publication_status
    success = False
    message = ""
    try:
        offer_is_test = await get_offer_is_test_by_offer_cian_id(offer_cian_id)
        if offer_is_test is False:
            message = f'Обьявление с offer_cian_id {offer_cian_id} не тестовое.'
        elif offer_is_test is None:
            message = f'Обьявление с offer_cian_id {offer_cian_id} не существует.'
        else:
            old_row_version = await get_offer_row_version_by_offer_cian_id(offer_cian_id)
            if old_row_version is None:
                message = f"Не существует обьявления с offer_cian_id {offer_cian_id}"
            elif old_row_version > row_version:
                message = f"new_version должен быть > {old_row_version}"
            else:
                await update_publication_status(
                    publication_status=publication_status,
                    row_version=row_version,
                    offer_cian_id=offer_cian_id,
                )
                success = True
                message = f'Успех! Статус был изменен на {publication_status.value}.'
    except PostgresError as e:
        message = str(e)
    return UpdateTestObjectsPublicationStatusResponse(
        success=success,
        message=message,
    )