import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

import pytz
from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException, BadRequestException, TimeoutException
from cian_kafka._producer.exceptions import KafkaProducerError
from simple_settings import settings

from external_offers import pg
from external_offers.entities.kafka import CallsKafkaMessage, DraftAnnouncementsKafkaMessage
from external_offers.entities.save_offer import DealType, OfferType, SaveOfferRequest, SaveOfferResponse
from external_offers.enums import CallStatus, OfferStatus, SaveOfferCategory, SaveOfferTerm
from external_offers.enums.save_offer_status import SaveOfferStatus
from external_offers.helpers import transform_phone_number_to_canonical_format
from external_offers.mappers import map_save_request_to_promocode_detail_model, map_save_request_to_publication_model
from external_offers.queue.kafka import kafka_preposition_calls_producer, kafka_preposition_drafts_producer
from external_offers.repositories.monolith_cian_announcementapi import v1_geo_geocode, v2_announcements_draft
from external_offers.repositories.monolith_cian_announcementapi.entities import (
    AddDraftResult,
    GeoCodeAnnouncementResponse,
    V1GeoGeocode,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import Category
from external_offers.repositories.monolith_cian_profileapi import promocode_apply
from external_offers.repositories.monolith_cian_profileapi.entities import ApplyParameters
from external_offers.repositories.monolith_cian_service import api_promocodes_create_promocode_group
from external_offers.repositories.monolith_cian_service.entities import CreatePromocodeGroupResponse
from external_offers.repositories.postgresql import (
    get_client_by_client_id,
    get_offer_by_offer_id,
    get_offer_cian_id_by_offer_id,
    get_offer_promocode_by_offer_id,
    get_segment_by_client_id,
    save_event_log_for_offers,
    set_client_accepted_and_no_operator_if_no_offers_in_progress,
    set_main_cian_user_id_by_client_id,
    set_offer_cian_id_by_offer_id,
    set_offer_draft_by_offer_id,
    set_offer_promocode_by_offer_id,
    try_to_lock_offer_and_return_status,
)
from external_offers.repositories.users import v1_register_user_by_phone, v2_get_users_by_phone
from external_offers.repositories.users.entities import (
    RegisterUserByPhoneRequest,
    RegisterUserByPhoneResponse,
    V2GetUsersByPhone,
)


category_mapping_key = Tuple[SaveOfferTerm, SaveOfferCategory, DealType, OfferType]
mapping_offer_params_to_category: Dict[category_mapping_key, Category] = {
    (SaveOfferTerm.long_term, SaveOfferCategory.flat, DealType.rent, OfferType.flat): Category.flat_rent,
    (None, SaveOfferCategory.flat, DealType.sale, OfferType.flat): Category.flat_sale,
    (None, SaveOfferCategory.bed, DealType.sale, OfferType.flat): Category.flat_share_sale,
    (None, SaveOfferCategory.share, DealType.sale, OfferType.flat): Category.flat_share_sale,
    (SaveOfferTerm.long_term, SaveOfferCategory.bed, DealType.rent, OfferType.flat): Category.bed_rent,
    (SaveOfferTerm.long_term, SaveOfferCategory.share, DealType.rent, OfferType.flat): Category.room_rent,
    (SaveOfferTerm.long_term, SaveOfferCategory.room, DealType.rent, OfferType.flat): Category.room_rent,
    (None, SaveOfferCategory.room, DealType.sale, OfferType.flat): Category.room_sale,
    (SaveOfferTerm.daily_term, SaveOfferCategory.flat, DealType.rent, OfferType.flat): Category.daily_flat_rent,
    (SaveOfferTerm.daily_term, SaveOfferCategory.room, DealType.rent, OfferType.flat): Category.daily_room_rent,
    (SaveOfferTerm.daily_term, SaveOfferCategory.bed, DealType.rent, OfferType.flat): Category.daily_bed_rent,
    (None, SaveOfferCategory.house, DealType.sale, OfferType.suburban): Category.house_sale,
    (None, SaveOfferCategory.cottage, DealType.sale, OfferType.suburban): Category.cottage_sale,
    (None, SaveOfferCategory.townhouse, DealType.sale, OfferType.suburban): Category.townhouse_sale,
    (None, SaveOfferCategory.land, DealType.sale, OfferType.suburban): Category.land_sale,
}


logger = logging.getLogger(__name__)


def statsd_incr_if_not_test_user(
    *,
    metric: str,
    user_id: int
) -> None:
    if user_id not in settings.TEST_OPERATOR_IDS:
        statsd.incr(metric)


async def save_offer_public(request: SaveOfferRequest, *, user_id: int) -> SaveOfferResponse:
    """ Сохранить объявление как черновик в ЦИАН. """
    async with pg.get().transaction():
        offer = await get_offer_by_offer_id(
            offer_id=request.offer_id
        )


        if not offer:
            return SaveOfferResponse(
                status=SaveOfferStatus.missing_offer,
                message='Отсутствует объявление с переданным идентификатором'
            )

        client = await get_client_by_client_id(client_id=request.client_id)

        status = await try_to_lock_offer_and_return_status(
                offer_id=request.offer_id
        )
        if not status:
            return SaveOfferResponse(
                status=SaveOfferStatus.already_processing,
                message='Объявление уже обрабатывается'
            )
        if status == OfferStatus.draft.value:
            return SaveOfferResponse(
                status=SaveOfferStatus.already_processed,
                message='Объявление уже сохранено как черновик'
            )

        phone_number = transform_phone_number_to_canonical_format(client.client_phones[0])
        cian_user_id = client.cian_user_id

        if not client.main_account_chosen:
            try:  # Регистрируем клиента по номеру телефона или получаем уже существующий аккаунт
                if request.account_for_draft and request.account_for_draft != cian_user_id:
                    now = datetime.now(tz=pytz.utc)
                    await kafka_preposition_calls_producer(
                        message=CallsKafkaMessage(
                            manager_id=user_id,
                            source_user_id=client.avito_user_id,
                            user_id=request.account_for_draft,
                            phone=phone_number,
                            status=CallStatus.main_account_changed,
                            call_id=offer.last_call_id,
                            date=now,
                            source=settings.AVITO_SOURCE_NAME
                        ),
                        timeout=settings.DEFAULT_KAFKA_TIMEOUT
                    )

                cian_user_id = request.account_for_draft or cian_user_id

                if request.create_new_account or not cian_user_id:
                    if not (cian_user_id := await cian_user_id_of_recently_registrated_account(phone_number)):
                        register_response: RegisterUserByPhoneResponse = await v1_register_user_by_phone(
                            RegisterUserByPhoneRequest(
                                phone=phone_number,
                                sms_template=runtime_settings.SMS_REGISTRATION_TEMPLATE
                            )
                        )
                        cian_user_id = register_response.user_data.id

                await set_main_cian_user_id_by_client_id(
                    cian_user_id=cian_user_id,
                    client_id=request.client_id
                )

            except ApiClientException as exc:
                statsd_incr_if_not_test_user(
                    metric='save_offer.error.registration',
                    user_id=user_id
                )
                logger.warning(
                    'Ошибка при создании учетной записи для объявления %s: %s',
                    request.offer_id,
                    exc.message
                )

                return SaveOfferResponse(
                    status=SaveOfferStatus.registration_failed,
                    message='Не удалось создать учетную запись по номеру телефона'
                )

        category = mapping_offer_params_to_category[
            (request.term_type,
             request.category,
             request.deal_type,
             request.offer_type)
        ]

        try:  # Геокодинг переданного через форму адреса
            geocode_response: GeoCodeAnnouncementResponse = await v1_geo_geocode(
                V1GeoGeocode(
                    request=request.address,
                    category=category
                )
            )
            if runtime_settings.get('CHECK_BILLING_REGION_ID', False):
                if geocode_response.billing_region_id == 0:
                    raise BadRequestException(
                        message='Невозможно опубликовать объявление с таким адресом, т.к.'
                                'это не поддерживается биллингом'
                    )
        except BadRequestException as exc:
            statsd_incr_if_not_test_user(
                metric='save_offer.error.geocode.badrequest',
                user_id=user_id
            )
            logger.warning(
                'Ошибка при обработке переданного адреса "%s" для объявления %s: %s',
                request.address,
                request.offer_id,
                exc.message
            )

            return SaveOfferResponse(
                status=SaveOfferStatus.geocode_failed,
                message=f'Не удалось обработать переданный в объявлении адрес. {exc.message}'
            )
        except TimeoutException as exc:
            statsd_incr_if_not_test_user(
                metric='save_offer.error.geocode.timeout',
                user_id=user_id
            )
            logger.warning(
                'Таймаут при обработке переданного адреса "%s" для объявления %s',
                request.address,
                request.offer_id
            )

            return SaveOfferResponse(
                status=SaveOfferStatus.geocode_failed,
                message='Не удалось обработать переданный в объявлении адрес за лимит времени. Попробуйте ещё раз'
            )

        try:  # Создание черновика объявления
            offer_cian_id = await get_offer_cian_id_by_offer_id(
                offer_id=request.offer_id
            )
            if not offer_cian_id:
                user_segment = await get_segment_by_client_id(
                    client_id=request.client_id
                )
                add_draft_result: AddDraftResult = await v2_announcements_draft(
                    map_save_request_to_publication_model(
                        request=request,
                        cian_user_id=cian_user_id,
                        geocode_response=geocode_response,
                        phone_number=phone_number,
                        category=category,
                        user_segment=user_segment
                    )
                )
                offer_cian_id = add_draft_result.realty_object_id
                await set_offer_cian_id_by_offer_id(
                    offer_cian_id=offer_cian_id,
                    offer_id=request.offer_id
                )
        except BadRequestException as exc:
            statsd_incr_if_not_test_user(
                metric='save_offer.error.draft_create.badrequest',
                user_id=user_id
            )
            logger.warning(
                'Ошибка при создании черновика для объявления %s: %s',
                request.offer_id,
                exc.message
            )

            return SaveOfferResponse(
                status=SaveOfferStatus.draft_failed,
                message=f'Не удалось создать черновик объявления. {exc.message}'
            )
        except TimeoutException as exc:
            statsd_incr_if_not_test_user(
                metric='save_offer.error.draft_create.timeout',
                user_id=user_id
            )
            logger.warning(
                'Таймаут при создании черновика для объявления %s',
                request.offer_id,
            )

            return SaveOfferResponse(
                status=SaveOfferStatus.draft_failed,
                message='Не удалось создать черновик за лимит времени. Попробуйте ещё раз'
            )

        # В конце location_path лежит идентификатор региона, используем его
        location_path = geocode_response.location_path
        if location_path and location_path[-1] in runtime_settings.REGIONS_WITH_PAID_PUBLICATION:
            try:  # Создание промокода на бесплатную публикацию объявления
                promocode = await get_offer_promocode_by_offer_id(
                    offer_id=request.offer_id
                )
                if not promocode:
                    promocode_response: CreatePromocodeGroupResponse = await api_promocodes_create_promocode_group(
                        map_save_request_to_promocode_detail_model(
                            request=request,
                            cian_user_id=cian_user_id
                        )
                    )
                    promocode = promocode_response.promocodes[0].promocode
                    await set_offer_promocode_by_offer_id(
                        promocode=promocode,
                        offer_id=request.offer_id
                    )
            except ApiClientException as exc:
                statsd_incr_if_not_test_user(
                    metric='save_offer.error.promo_create',
                    user_id=user_id
                )
                logger.warning(
                    'Ошибка при создании промокода на бесплатную публикацию для объявления %s: %s',
                    request.offer_id,
                    exc.message
                )

                return SaveOfferResponse(
                    status=SaveOfferStatus.promo_creation_failed,
                    message='Не удалось создать промокод на бесплатную публикацию'
                )

            try:  # Применение промокода на бесплатную публикацию объявления
                await promocode_apply(
                    ApplyParameters(
                        cian_user_id=cian_user_id,
                        promo_code=promocode
                    ))
            except ApiClientException as exc:
                statsd_incr_if_not_test_user(
                    metric='save_offer.error.promo_apply',
                    user_id=user_id
                )
                logger.warning(
                    'Ошибка при применении промокода на бесплатную публикацию для объявления %s: %s',
                    request.offer_id,
                    exc.message
                )
                return SaveOfferResponse(
                    status=SaveOfferStatus.promo_activation_failed,
                    message='Не удалось применить промокод на бесплатную публикацию'
                )

        await set_offer_draft_by_offer_id(offer_id=request.offer_id)
        await save_event_log_for_offers(
            offers_ids=[request.offer_id],
            call_id=offer.last_call_id,
            operator_user_id=user_id,
            status=OfferStatus.draft.value
        )

        updated = await set_client_accepted_and_no_operator_if_no_offers_in_progress(client_id=request.client_id)

        statsd_incr_if_not_test_user(
            metric='save_offer.success',
            user_id=user_id
        )
        if user_id not in settings.TEST_OPERATOR_IDS:
            now = datetime.now(tz=pytz.utc)
            try:
                await kafka_preposition_drafts_producer(DraftAnnouncementsKafkaMessage(
                    manager_id=user_id,
                    source_user_id=client.avito_user_id,
                    user_id=cian_user_id,
                    phone=phone_number,
                    call_id=offer.last_call_id,
                    date=now,
                    draft=offer_cian_id
                ))

                if updated:
                    await kafka_preposition_calls_producer(
                        message=CallsKafkaMessage(
                            manager_id=user_id,
                            source_user_id=client.avito_user_id,
                            user_id=cian_user_id,
                            phone=phone_number,
                            status=CallStatus.accepted,
                            call_id=offer.last_call_id,
                            date=now,
                            source=settings.AVITO_SOURCE_NAME
                        ),
                        timeout=settings.DEFAULT_KAFKA_TIMEOUT
                    )
            except KafkaProducerError:
                logger.warning('Не удалось отправить событие аналитики для объявления %s', request.offer_id)

        return SaveOfferResponse(
            status=SaveOfferStatus.ok,
            message='Объявление успешно создано'
        )


async def cian_user_id_of_recently_registrated_account(
    phone_number: str
) -> Optional[int]:
    response = await v2_get_users_by_phone(
        V2GetUsersByPhone(
            phone=phone_number
        )
    )
    users = response.users or []
    minutes = runtime_settings.RECENTLY_REGISTRATION_CHECK_DELAY
    dt = datetime.utcnow() - timedelta(minutes=minutes)
    for user in users:
        if user.creation_date >= dt:
            return user.cian_user_id
    return None
