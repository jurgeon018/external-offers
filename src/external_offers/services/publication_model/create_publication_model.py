from typing import Optional

from simple_settings import settings

from external_offers.entities.save_offer import SaveOfferRequest
from external_offers.helpers.phonenumber import (
    get_country_code_from_phone_number,
    get_phone_number_without_country_code,
)
from external_offers.helpers.uuid import generate_uppercase_guid
from external_offers.repositories.monolith_cian_announcementapi.entities import (
    BargainTerms,
    Building,
    GeoCodeAnnouncementResponse,
    ObjectModel,
    Phone,
    PublicationModel,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.bargain_terms import Currency, UtilitiesTerms
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import (
    Category,
    FlatType,
    PropertyType,
    SwaggerGeo,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.publication_model import Platform
from external_offers.repositories.monolith_cian_announcementapi.entities.swagger_geo import AddressInfo, Coordinates
from external_offers.services.publication_model.constants import (
    _CALLTRACKING_DISABLED,
    _NO_PREPAY_MONTH,
    _NOT_HOMEOWNER,
    _ONE_ROOM,
    _ZERO_ROW_VERSION,
)
from external_offers.services.publication_model.mappings import (
    geo_type_value_to_type_mapping,
    save_offer_realty_type_to_is_apartments_mapping,
    save_offer_rooms_count_to_flat_type_mapping,
    save_offer_rooms_count_to_num_mapping,
    save_offer_sale_type_to_sale_type_mapping,
    segment_to_homeowner_mapping,
)


def create_publication_model(
        request: SaveOfferRequest,
        cian_user_id: int,
        geocode_response: GeoCodeAnnouncementResponse,
        phone_number: str,
        category: Category,
        user_segment: Optional[str]
):
    return PublicationModel(
        model=ObjectModel(
            bargain_terms=BargainTerms(
                price=request.price,
                currency=Currency.rur,
                deposit=request.deposit,
                prepay_months=request.prepay_months if request.prepay_months != _NO_PREPAY_MONTH else None,
                sale_type=save_offer_sale_type_to_sale_type_mapping.get(request.sale_type, None),
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
            is_apartments=save_offer_realty_type_to_is_apartments_mapping.get(request.realty_type, None),
            property_type=PropertyType.building,
            rooms_count=save_offer_rooms_count_to_num_mapping.get(request.rooms_count, _ONE_ROOM),
            floor_number=request.floor_number,
            category=category,
            cian_user_id=cian_user_id,
            phones=[
                Phone(
                    number=get_phone_number_without_country_code(phone_number),
                    country_code=get_country_code_from_phone_number(phone_number)
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
                        type=geo_type_value_to_type_mapping.get(detail.geo_type.value)
                    ) for detail in geocode_response.details
                ]
            ),
            name=settings.DEFAULT_OFFER_DRAFT_NAME,
            description=request.description,
            object_guid=generate_uppercase_guid(),
            flat_type=save_offer_rooms_count_to_flat_type_mapping.get(request.rooms_count, FlatType.rooms),
            is_by_home_owner=segment_to_homeowner_mapping.get(user_segment, _NOT_HOMEOWNER),
            is_enabled_call_tracking=_CALLTRACKING_DISABLED,
            row_version=_ZERO_ROW_VERSION
        ),
        platform=Platform.web_site
    )
