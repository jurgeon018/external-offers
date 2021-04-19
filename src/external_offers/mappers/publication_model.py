from typing import Any, Dict, Optional

from external_offers.entities.save_offer import SaveOfferRequest
from external_offers.helpers.uuid import generate_uppercase_guid
from external_offers.repositories.monolith_cian_announcementapi.entities import (
    BargainTerms,
    Building,
    GeoCodeAnnouncementResponse,
    ObjectModel,
    Phone,
    PublicationModel,
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


geo_type_to_type_mapping: Dict[GeoType, Type] = {
    GeoType.house.value: Type.house,
    GeoType.country.value: Type.country,
    GeoType.district.value: Type.district,
    GeoType.road.value: Type.road,
    GeoType.street.value: Type.street,
    GeoType.underground.value: Type.underground,
    GeoType.location.value: Type.location
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

save_offer_sale_type_to_sale_type: Dict[str, SaleType] = {
    'free': SaleType.free,
    'alternative': SaleType.alternative
}

segment_to_is_by_homeowner: Dict[Any, bool] = {
    'a': False,
    'b': False,
    'c': False,
    'd': True
}


def map_save_request_to_publication_model(
    *,
    request: SaveOfferRequest,
    cian_user_id: int,
    geocode_response: GeoCodeAnnouncementResponse,
    phone_number: str,
    category: Category,
    user_segment: Optional[str]
) -> PublicationModel:
    is_by_home_owner = (request.publish_as_homeowner
                        if request.publish_as_homeowner is not None
                        else segment_to_is_by_homeowner.get(user_segment, False))

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
            rooms_count=rooms_count_to_num.get(request.rooms_count, 1),
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
            object_guid=generate_uppercase_guid(),
            flat_type=rooms_count_to_flat_type.get(request.rooms_count, FlatType.rooms),
            is_by_home_owner=is_by_home_owner,
            is_enabled_call_tracking=False,  # если этот параметр не слать, шарп 500ит
            row_version=0  # если этот параметр не слать, шарп 500ит
        ),
        platform=Platform.web_site  # если этот параметр не слать, шарп 500ит
    )
