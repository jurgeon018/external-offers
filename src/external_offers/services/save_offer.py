import logging
from datetime import datetime, timedelta
from typing import Dict, Tuple
from uuid import uuid4

import pytz
from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException, BadRequestException, TimeoutException
from cian_kafka._producer.exceptions import KafkaProducerError
from simple_settings import settings

from external_offers import pg
from external_offers.entities.kafka import CallsKafkaMessage, DraftAnnouncementsKafkaMessage
from external_offers.entities.save_offer import DealType, OfferType, SaveOfferRequest, SaveOfferResponse
from external_offers.enums import ClientStatus, OfferStatus, SaveOfferCategory
from external_offers.enums.save_offer_status import SaveOfferStatus
from external_offers.helpers import transform_phone_number_to_canonical_format
from external_offers.queue.kafka import kafka_preposition_calls_producer, kafka_preposition_drafts_producer
from external_offers.repositories.monolith_cian_announcementapi import v1_geo_geocode, v2_announcements_draft
from external_offers.repositories.monolith_cian_announcementapi.entities import (
    AddDraftResult,
    BargainTerms,
    Building,
    GeoCodeAnnouncementResponse,
    ObjectModel,
    Phone,
    PublicationModel,
    V1GeoGeocode,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.address_info import Type
from external_offers.repositories.monolith_cian_announcementapi.entities.bargain_terms import (
    Currency,
    SaleType,
    UtilitiesTerms,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.details import GeoType
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import (
    Category,
    FlatType,
    PropertyType,
    SwaggerGeo,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.publication_model import Platform
from external_offers.repositories.monolith_cian_announcementapi.entities.swagger_geo import AddressInfo, Coordinates
from external_offers.repositories.monolith_cian_profileapi import promocode_apply
from external_offers.repositories.monolith_cian_profileapi.entities import ApplyParameters
from external_offers.repositories.monolith_cian_service import api_promocodes_create_promocode_group
from external_offers.repositories.monolith_cian_service.entities import (
    CreatePromocodeGroupResponse,
    PromoCodeGroupDetailModel,
)
from external_offers.repositories.monolith_cian_service.entities.promo_code_group_detail_model import (
    PromoCodeGroupModel,
    ServicePackageStrategyModel,
)
from external_offers.repositories.monolith_cian_service.entities.promo_code_group_model import Source
from external_offers.repositories.monolith_cian_service.entities.promo_code_group_model import Type as PromoType
from external_offers.repositories.monolith_cian_service.entities.service_package_strategy_item_model import (
    DurationInDays,
    ObjectTypeId,
    OperationTypes,
)
from external_offers.repositories.monolith_cian_service.entities.service_package_strategy_model import (
    ServicePackageStrategyItemModel,
)
from external_offers.repositories.monolith_cian_service.entities.service_package_strategy_model import (
    Type as StartegyType,
)
from external_offers.repositories.postgresql import (
    get_cian_user_id_by_client_id,
    get_client_by_client_id,
    get_offer_cian_id_by_offer_id,
    get_offer_promocode_by_offer_id,
    save_event_log_for_offers,
    set_cian_user_id_by_client_id,
    set_client_accepted_and_no_operator_if_no_offers_in_progress,
    set_offer_cian_id_by_offer_id,
    set_offer_draft_by_offer_id,
    set_offer_promocode_by_offer_id,
    try_to_lock_offer_and_return_status,
)
from external_offers.repositories.users import v1_register_user_by_phone
from external_offers.repositories.users.entities import RegisterUserByPhoneRequest, RegisterUserByPhoneResponse


geo_type_to_type_mapping: Dict[GeoType, Type] = {
    GeoType.house.value: Type.house,
    GeoType.country.value: Type.country,
    GeoType.district.value: Type.district,
    GeoType.road.value: Type.road,
    GeoType.street.value: Type.street,
    GeoType.underground.value: Type.underground,
    GeoType.location.value: Type.location
}

offer_type_to_object_type: Dict[OfferType, ObjectTypeId] = {
    OfferType.commercial: ObjectTypeId.commercial,
    OfferType.flat: ObjectTypeId.flat,
    OfferType.suburban: ObjectTypeId.suburbian,
    OfferType.newobject: ObjectTypeId.flat
}

category_mapping_key = Tuple[SaveOfferCategory, DealType, OfferType]
save_offer_category_deal_type_and_offer_type_to_category: Dict[category_mapping_key, Category] = {
    (SaveOfferCategory.flat, DealType.rent, OfferType.flat): Category.flat_rent,
    (SaveOfferCategory.flat, DealType.sale, OfferType.flat): Category.flat_sale,
    (SaveOfferCategory.bed, DealType.sale, OfferType.flat): Category.flat_share_sale,
    (SaveOfferCategory.bed, DealType.rent, OfferType.flat): Category.bed_rent,
    (SaveOfferCategory.share, DealType.sale, OfferType.flat): Category.flat_share_sale,
    (SaveOfferCategory.share, DealType.rent, OfferType.flat): Category.room_rent,
    (SaveOfferCategory.room, DealType.rent, OfferType.flat): Category.room_rent,
    (SaveOfferCategory.room, DealType.sale, OfferType.flat): Category.room_sale,
}

deal_type_to_operation_types = {
    DealType.sale: OperationTypes.sale,
    DealType.rent: OperationTypes.rent
}

rooms_count_to_num: Dict[str, int] = {
    'room1': 1,
    'room2': 2,
    'room3': 3,
    'room4': 4,
    'room5': 5,
    'room6_plus': 6,
    'open_plan': 1,
    'studio': 1
}

rooms_count_to_flat_type: Dict[str, FlatType] = {
    'room1': FlatType.rooms,
    'room2': FlatType.rooms,
    'room3': FlatType.rooms,
    'room4': FlatType.rooms,
    'room5': FlatType.rooms,
    'room6_plus': FlatType.rooms,
    'open_plan': FlatType.open_plan,
    'studio': FlatType.studio

}

realty_type_to_is_aparments: Dict[str, bool] = {
    'apartments': True,
    'flat': False
}

save_offer_sale_type_to_sale_type = {
    'free': SaleType.free,
    'alternative': SaleType.alternative
}

logger = logging.getLogger(__name__)

def create_publication_model(
        request: SaveOfferRequest,
        cian_user_id: int,
        geocode_response: GeoCodeAnnouncementResponse,
        phone_number: str,
        category: Category,

):
    return PublicationModel(
        model=ObjectModel(
            bargain_terms=BargainTerms(
                price=request.price,
                currency=Currency.rur,
                deposit=request.deposit,
                prepay_months=request.prepay_months if request.prepay_months != 0 else None,
                sale_type=save_offer_sale_type_to_sale_type.get(request.sale_type, None),
                utilities_terms=[
                    UtilitiesTerms(
                        included_in_price=True
                    )
                ]
            ),
            building=Building(
                floors_count=request.floors_count
            ),
            total_area=request.total_area,
            is_apartments=realty_type_to_is_aparments.get(request.realty_type, None),
            property_type=PropertyType.building,
            rooms_count=rooms_count_to_num.get(request.rooms_count, None),
            floor_number=request.floor_number,
            category=category,
            cian_user_id=cian_user_id,
            phones=[
                Phone(
                    number=phone_number[2:],
                    country_code=phone_number[:2]
                )
            ],
            geo=SwaggerGeo(
                country_id=geocode_response.country_id,
                coordinates=Coordinates(
                    lat=geocode_response.geo.lat,
                    lng=geocode_response.geo.lng
                ),
                user_input=request.address,
                address=[
                    AddressInfo(
                        id=detail.id,
                        type=geo_type_to_type_mapping[detail.geo_type.value]
                    ) for detail in geocode_response.details
                ]
            ),
            name='Наименование',
            description=request.description,
            object_guid=str(uuid4()).upper(),
            flat_type=rooms_count_to_flat_type.get(request.rooms_count, None),
            is_enabled_call_tracking=False,  # если этот параметр не слать, шарп 500ит
            row_version=0  # если этот параметр не слать, шарп 500ит
        ),
        platform=Platform.web_site  # если этот параметр не слать, шарп 500ит
    )


def create_promocode_detail_model(
        request: SaveOfferRequest,
        cian_user_id: int
):
    now = datetime.now(tz=pytz.utc)

    return PromoCodeGroupDetailModel(
        promo_code_group_model=PromoCodeGroupModel(
            name=settings.PROMOCODE_GROUP_NAME,
            source=Source.other,
            type=PromoType.service_package,
            for_specific_user_ids=True,
            available_to=(now + timedelta(days=1)),
            promo_codes_count=1,
            cian_user_ids=str(cian_user_id)
        ),
        service_package_strategy=ServicePackageStrategyModel(
            is_paid=False,
            auto_activate_for_manual_announcements=False,
            activations_count=1,
            type=StartegyType.publication,
            items=[ServicePackageStrategyItemModel(
                operation_types=[
                    OperationTypes.sale,
                    OperationTypes.rent
                ],
                polygon_ids=settings.PROMOCODE_POLYGONS,
                duration_in_days=DurationInDays.seven,
                debit_count=1,
                object_type_id=offer_type_to_object_type[request.offer_type]
            )]
        )
    )


def statsd_incr_if_not_test_user(metric: str, user_id: int):
    if user_id not in settings.TEST_OPERATOR_IDS:
        statsd.incr(metric)


async def save_offer_public(request: SaveOfferRequest, *, user_id: int) -> SaveOfferResponse:
    """ Сохранить объявление как черновик в ЦИАН. """
    async with pg.get().transaction():
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

        phone_number = transform_phone_number_to_canonical_format(request.phone_number)
        category = save_offer_category_deal_type_and_offer_type_to_category[
            (request.category,
             request.deal_type,
             request.offer_type)
        ]

        try:  # Регистрируем клиента по номеру телефона или получаем уже существующий аккаунт
            cian_user_id = await get_cian_user_id_by_client_id(
                client_id=request.client_id
            )
            if not cian_user_id:
                register_response: RegisterUserByPhoneResponse = await v1_register_user_by_phone(
                    RegisterUserByPhoneRequest(
                        phone=phone_number,
                        sms_template=settings.SMS_REGISTRATION_TEMPLATE
                    )
                )
                cian_user_id = register_response.user_data.id
                await set_cian_user_id_by_client_id(
                    cian_user_id=cian_user_id,
                    client_id=request.client_id
                )

                if register_response.has_many_accounts:
                    logger.warning(
                        'Не удалось однозначно определить аккаунт для пользователя %s, выбран %d',
                        request.client_id,
                        cian_user_id
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

        try:  # Геокодинг переданного через форму адреса
            geocode_response: GeoCodeAnnouncementResponse = await v1_geo_geocode(
                V1GeoGeocode(
                    request=request.address,
                    category=category
                )
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
                metric='save_offer.error.geocode',
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
                add_draft_result: AddDraftResult = await v2_announcements_draft(create_publication_model(
                    request=request,
                    cian_user_id=cian_user_id,
                    geocode_response=geocode_response,
                    phone_number=phone_number,
                    category=category
                ))
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
        if geocode_response.location_path[-1] in settings.REGIONS_WITH_PAID_PUBLICATION:
            try:  # Создание промокода на бесплатную публикацию объявления
                promocode = await get_offer_promocode_by_offer_id(
                    offer_id=request.offer_id
                )
                if not promocode:
                    promocode_response: CreatePromocodeGroupResponse = await api_promocodes_create_promocode_group(
                        create_promocode_detail_model(
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
            operator_user_id=user_id,
            status=OfferStatus.draft.value
        )
        client = await get_client_by_client_id(client_id=request.client_id)

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
                    date=now,
                    draft=offer_cian_id
                ))

                if updated:
                    await kafka_preposition_calls_producer(
                        message=CallsKafkaMessage(
                            manager_id=user_id,
                            source_user_id=client.avito_user_id,
                            user_id=client.cian_user_id,
                            phone=client.client_phones[0],
                            status=ClientStatus.accepted.value,
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
