import logging
from typing import Dict, Optional

from cian_http.exceptions import ApiClientException
from simple_settings import settings

from external_offers.entities.parsed_offers import ParsedOffer, ParsedOfferMessage
from external_offers.helpers import transform_phone_number_to_canonical_format
from external_offers.queue.entities import SourceModel
from external_offers.queue.producers import external_offers_change_producer
from external_offers.repositories import postgresql
from external_offers.repositories.monolith_cian_announcementapi.entities import (
    AddressInfo,
    BargainTerms,
    Building,
    Coordinates,
    ObjectModel,
    Phone,
    SwaggerGeo,
    UtilitiesTerms,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.bargain_terms import Currency
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import Category, PropertyType
from external_offers.repositories.monolith_cian_geoapi import v2_geocode
from external_offers.repositories.monolith_cian_geoapi.entities import GeoCodedRequest
from external_offers.services.save_offer import geo_type_to_type_mapping


logger = logging.getLogger(__name__)

SOURCE_ROOMS_COUNT = 'roomsCount'
SOURCE_TOTAL_AREA = 'totalArea'
SOURCE_LIVING_AREA = 'livingArea'
SOURCE_FLOORS_COUNT = 'floorsCount'
SOURCE_PRICE = 'price'
SOURCE_DESCRIPTION = 'description'
SOURCE_FLOOR_NUMBER = 'floorNumber'
SOURCE_CATEGORY = 'category'
SOURCE_PHONES = 'phones'
SOURCE_ADDRESS = 'address'
SOURCE_LAT = 'lat'
SOURCE_LNG = 'lng'
SOURCE_URL = 'url'
SOURCE_IS_AGENCY = 'isAgency'

DEFAULT_GEOCODE_KIND = 'house'

SOURCE_CATEGORY_TO_CATEGORY: Dict[str, Category] = {
    'flatSale': Category.flat_sale,
    'flatRent': Category.flat_rent,
}

CITY_LOCATION_ID = 1
REGION_LOCATION_ID = 2


def get_rooms_count_from_source_object_model(source_object_model: dict) -> Optional[int]:
    return source_object_model.get(SOURCE_ROOMS_COUNT)


def get_total_area_from_source_object_model(source_object_model: dict) -> Optional[float]:
    return source_object_model.get(SOURCE_TOTAL_AREA)


def get_living_area_from_source_object_model(source_object_model: dict) -> Optional[float]:
    return source_object_model.get(SOURCE_LIVING_AREA)


def get_floors_count_from_source_object_model(source_object_model: dict) -> Optional[int]:
    return source_object_model.get(SOURCE_FLOORS_COUNT)


def get_price_from_source_object_model(source_object_model: dict) -> Optional[int]:
    return source_object_model.get(SOURCE_PRICE)


def get_floor_number_from_source_object_model(source_object_model: dict) -> Optional[int]:
    return source_object_model.get(SOURCE_FLOOR_NUMBER)


def get_description_from_source_object_model(source_object_model: dict) -> Optional[str]:
    return source_object_model.get(SOURCE_DESCRIPTION)


def get_category_from_source_object_model(source_object_model: dict) -> Optional[Category]:
    return SOURCE_CATEGORY_TO_CATEGORY.get(str(source_object_model.get(SOURCE_CATEGORY)))


def get_lat_from_source_object_model(source_object_model: dict) -> Optional[float]:
    return source_object_model.get(SOURCE_LAT)


def get_lng_from_source_object_model(source_object_model: dict) -> Optional[float]:
    return source_object_model.get(SOURCE_LNG)


def get_address_from_source_object_model(source_object_model: dict) -> Optional[str]:
    return source_object_model.get(SOURCE_ADDRESS)


def get_is_by_homeowner_from_source_object_model(source_object_model: dict) -> Optional[bool]:
    is_agency = bool(source_object_model.get(SOURCE_IS_AGENCY))
    return not is_agency


def get_id_from_source_object_id(source_object_id: str) -> str:
    return source_object_id.split(sep='_')[1]


async def get_geo_by_source_object_model(source_object_model: dict) -> Optional[SwaggerGeo]:
    lng = get_lng_from_source_object_model(source_object_model)
    lat = get_lat_from_source_object_model(source_object_model)
    if not (lat and lng):
        return None

    try:
        geocode_response = await v2_geocode(GeoCodedRequest(
            kind=DEFAULT_GEOCODE_KIND,
            lat=lat,
            lng=lng
        ))
    except ApiClientException:
        return None
    address = []
    for detail in geocode_response.details:
        location_type_id = None
        _type = geo_type_to_type_mapping[detail.geo_type.value]

        if _type.is_location and detail.is_locality:
            location_type_id = CITY_LOCATION_ID

        if _type.is_location and not detail.is_locality:
            location_type_id = REGION_LOCATION_ID

        address.append(AddressInfo(
            id=detail.id,
            full_name=detail.full_name,
            short_name=detail.name,
            name=detail.name,
            type=_type,
            location_type_id=location_type_id,
            is_forming_address=True,
        ))

    return SwaggerGeo(
        country_id=geocode_response.country_id,
        coordinates=Coordinates(
            lat=geocode_response.geo.lat,
            lng=geocode_response.geo.lng
        ),
        user_input=get_address_from_source_object_model(source_object_model),
        address=address
    )


def get_phone_from_source_object_model(source_object_model: dict) -> Optional[str]:
    source_phones = source_object_model.get(SOURCE_PHONES)
    if not source_phones:
        return None

    return transform_phone_number_to_canonical_format(source_phones[0])


def create_source_model_from_parsed_offer(*, offer: ParsedOffer) -> SourceModel:
    return SourceModel(
        source=settings.AVITO_SOURCE_NAME,
        source_object_id=offer.source_object_id,
        timestamp=offer.timestamp,
        external_url=offer.source_object_model.get(SOURCE_URL)
    )


def offer_is_suitable(source_object_model: dict) -> bool:
    return source_object_model.get(SOURCE_CATEGORY) in settings.SUITABLE_CATEGORIES_FOR_REPORTING


async def create_object_model_from_parsed_offer(*, offer: ParsedOffer) -> Optional[ObjectModel]:
    source_object_model = offer.source_object_model

    if not offer_is_suitable(source_object_model):
        return None

    phone_number = get_phone_from_source_object_model(source_object_model)
    if not phone_number:
        logger.warning('Отсутствует номера телефона у объявления %s', offer.source_object_id)
        return None

    geo = await get_geo_by_source_object_model(source_object_model)
    if not geo:
        logger.warning('Не удалось получить гео для объявления %s', offer.source_object_id)
        return None

    return ObjectModel(
            id=get_id_from_source_object_id(offer.source_object_id),
            bargain_terms=BargainTerms(
                price=get_price_from_source_object_model(source_object_model),
                currency=Currency.rur,
                utilities_terms=[
                    UtilitiesTerms(
                        included_in_price=True
                    )
                ],
            ),
            building=Building(
                floors_count=get_floors_count_from_source_object_model(source_object_model)
            ),
            phones=[
                Phone(
                    number=phone_number[2:],
                    country_code=phone_number[:2]
                )
            ],
            total_area=get_total_area_from_source_object_model(source_object_model),
            living_area=get_living_area_from_source_object_model(source_object_model),
            property_type=PropertyType.building,
            rooms_count=get_rooms_count_from_source_object_model(source_object_model),
            floor_number=get_floor_number_from_source_object_model(source_object_model),
            category=get_category_from_source_object_model(source_object_model),
            geo=geo,
            description=get_description_from_source_object_model(source_object_model),
            is_enabled_call_tracking=offer.is_calltracking,
            is_by_home_owner=get_is_by_homeowner_from_source_object_model(source_object_model),
            row_version=0
    )


async def save_parsed_offer(*, offer: ParsedOfferMessage) -> None:
    """ Сохранить объявление с внешней площадки. """
    await postgresql.save_parsed_offer(parsed_offer=offer)


async def send_parsed_offer_change_event(*, offer: ParsedOfferMessage) -> None:
    """ Преобразовать ParsedOffer в ObjectModel и оповестить """
    object_model = await create_object_model_from_parsed_offer(
        offer=offer
    )

    if not object_model:
        return None

    source_model = create_source_model_from_parsed_offer(
        offer=offer
    )

    await external_offers_change_producer(
        model=object_model,
        source_model=source_model
    )
