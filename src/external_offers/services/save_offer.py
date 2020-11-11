from datetime import datetime, timedelta
from uuid import uuid4

import pytz
from cian_http.exceptions import BadRequestException, ApiClientException
from simple_settings import settings

from external_offers.entities.save_offer import SaveOfferRequest, SaveOfferResponse
from external_offers.enums import BillingPolygon
from external_offers.enums.save_offer_status import SaveOfferStatus
from external_offers.helpers import transform_phone_number_to_canonical_format
from external_offers.repositories.monolith_cian_announcementapi import v1_geo_geocode, v2_announcements_draft
from external_offers.repositories.monolith_cian_announcementapi.entities import (
    AddDraftResult,
    BargainTerms,
    GeoCodeAnnouncementResponse,
    ObjectModel,
    Phone,
    PublicationModel,
    V1GeoGeocode,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.details import GeoType
from external_offers.repositories.monolith_cian_announcementapi.entities.address_info import Type
from external_offers.repositories.monolith_cian_announcementapi.entities.bargain_terms import Currency
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import (
    Category,
    FlatType,
    PropertyType,
    Status,
    SwaggerGeo,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.publication_model import Platform
from external_offers.repositories.monolith_cian_announcementapi.entities.swagger_geo import AddressInfo, Coordinates
from external_offers.repositories.monolith_cian_bill._repo import v1_service_packages_buy_subscription_package
from external_offers.repositories.monolith_cian_bill.entities import (
    AddServicePackageResponse,
    BuySubscriptionPackageRequest,
    ServicePackageItem,
)
from external_offers.repositories.monolith_cian_bill.entities.buy_subscription_package_request import (
    ServicePackageStrategyType,
)
from external_offers.repositories.monolith_cian_bill.entities.service_package_item import ServiceTypes
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
    OperationTypeId,
    OperationTypes,
)
from external_offers.repositories.monolith_cian_service.entities.service_package_strategy_model import (
    ServicePackageStrategyItemModel,
)
from external_offers.repositories.monolith_cian_service.entities.service_package_strategy_model import (
    Type as StartegyType,
)
from external_offers.repositories.postgresql import set_offer_draft_by_offer_id
from external_offers.repositories.users import v1_register_user_by_phone
from external_offers.repositories.users.entities import RegisterUserByPhoneRequest, RegisterUserByPhoneResponse


property_type_mapping = {

}

geo_type_to_type_mapping = {
    GeoType.house: Type.house,
    GeoType.country: Type.country,
    GeoType.district: Type.district,
    GeoType.road: Type.road,
    GeoType.street: Type.street,
    GeoType.underground: Type.underground,
    GeoType.location: Type.location
}

async def save_offer_public(request: SaveOfferRequest, *, user_id: int) -> SaveOfferResponse:
    """ Сохранить объявление как черновик в ЦИАН. """
    request.phone_number =  transform_phone_number_to_canonical_format(request.phone_number)
    try:
        register_response: RegisterUserByPhoneResponse = await v1_register_user_by_phone(
            RegisterUserByPhoneRequest(
                phone='+79819547472',
                sms_template=None
            )
        )
    except ApiClientException:
        return SaveOfferResponse(
            status=SaveOfferStatus.registration_failed,
            message='Не удалось создать учетную запись по номеру телефона'
        )


    try:
        geocode_response: GeoCodeAnnouncementResponse = await v1_geo_geocode(
            V1GeoGeocode(
                request=request.address,
                category=Category.flat_rent
            )
        )
    except ApiClientException:
        return SaveOfferResponse(
            status=SaveOfferStatus.geocode_failed,
            message='Не удалось обработать переданный в объявлении адрес'
        )

    try:
        add_draft_response: AddDraftResult = await v2_announcements_draft(PublicationModel(
            model=ObjectModel(
                bargain_terms=BargainTerms(
                    price = request.price,
                    currency=Currency.rur
                ),
                total_area=request.total_area,
                property_type=PropertyType.building,
                rooms_count=6,
                floor_number=request.floor_number,
                category=Category.flat_sale,
                user_id=register_response.user_data.id,
                phones=[
                    Phone(
                        number='9819547472',
                        country_code='+7'
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
                            type=geo_type_to_type_mapping[detail.geo_type]
                        ) for detail in geocode_response.details
                    ]
                ),
                name='Наименование',
                title='Черновик объявления',
                description='Описание черновика объявления!',
                object_guid=str(uuid4()).upper(),
                flat_type=FlatType.rooms,
                is_enabled_call_tracking=False, # если этот параметр не слать, шарп 500ит
                row_version=0 # если этот параметр не слать, шарп 500ит
            ),
            platform=Platform.web_site # если этот параметр не слать, шарп 500ит
        ))
    except ApiClientException:
        return SaveOfferResponse(
            status=SaveOfferStatus.draft_failed,
            message='Не удалось создать черновик объявления'
        )
    now = datetime.now(tz=pytz.utc)
    try:
        promocode_response: CreatePromocodeGroupResponse = await api_promocodes_create_promocode_group(
            PromoCodeGroupDetailModel(
                promo_code_group_model=PromoCodeGroupModel(
                    name=settings.PROMOCODE_GROUP_NAME,
                    source=Source.other,
                    type=PromoType.service_package,
                    for_specific_user_ids=True,
                    available_to=(now + timedelta(days=1)),
                    promo_codes_count=1,
                    cian_user_ids=str(register_response.user_data.id)
                ),
                service_package_strategy=ServicePackageStrategyModel(
                    is_paid=False,
                    auto_activate_for_manual_announcements=False,
                    activations_count=1,
                    type=StartegyType.publication,
                    items=[ServicePackageStrategyItemModel(
                        operation_types=[
                            OperationTypes.rent,
                            OperationTypes.sale
                        ],
                        polygon_ids=[
                            BillingPolygon.Moscow.value
                        ],
                        duration_in_days=DurationInDays.seven,
                        debit_count=1,
                        operation_type_id=OperationTypeId.sale,
                        object_type_id=ObjectTypeId.any
                    )]
                )
            )
        )
    except ApiClientException:
        return SaveOfferResponse(
            status=SaveOfferStatus.promo_creation_failed,
            message='Не удалось создать промокод на бесплатную публикацию'
        )

    try:
        apply_response = await promocode_apply(
            ApplyParameters(
                cian_user_id=register_response.user_data.id,
                promo_code=promocode_response.promocodes[0].promocode
            ))
    except ApiClientException:
        return SaveOfferResponse(
            status=SaveOfferStatus.promo_activation_failed,
            message='Не удалось применить промокод на бесплатные публикации'
        )

    await set_offer_draft_by_offer_id(offer_id=request.offer_id)

    return SaveOfferResponse(status=SaveOfferStatus.ok)


# {
#         "id": 1,
#         "type": "location"
#       },
#       {
#         "id": 3210,
#         "type": "street"
#       },
#       {
#         "id": 61776,
#         "type": "house"
#       }
