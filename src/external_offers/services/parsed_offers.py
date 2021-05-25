import logging
from typing import Dict, Optional

from cian_core.runtime_settings import runtime_settings
from cian_core.statsd import statsd
from cian_http.exceptions import ApiClientException
from simple_settings import settings

from external_offers.entities.parsed_offers import ParsedOffer, ParsedOfferMessage
from external_offers.helpers import transform_phone_number_to_canonical_format
from external_offers.mappers.publication_model import geo_type_to_type_mapping
from external_offers.queue.entities import SourceModel
from external_offers.queue.producers import external_offers_change_producer
from external_offers.repositories import postgresql
from external_offers.repositories.monolith_cian_announcementapi.entities import (
    AddressInfo,
    BargainTerms,
    Building,
    Coordinates,
    DistrictInfo,
    ObjectModel,
    Phone,
    SwaggerGeo,
    UtilitiesTerms,
)
from external_offers.repositories.monolith_cian_announcementapi.entities.bargain_terms import Currency
from external_offers.repositories.monolith_cian_announcementapi.entities.district_info import Type as DistrictType
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import (
    Category,
    FlatType,
    PropertyType,
)
from external_offers.repositories.monolith_cian_geoapi import v2_geocode
from external_offers.repositories.monolith_cian_geoapi.entities import GeoCodedRequest
from external_offers.repositories.monolith_cian_geoapi.entities.get_districts_response import Type as GetDistrictsType
from external_offers.services.districts import get_districts_by_district_ids_cached, get_districts_by_house_id_cached
from external_offers.services.districts.exceptions import GetDistrictsError
from external_offers.services.undergrounds.get_undergrounds import get_underground_by_coordinates


logger = logging.getLogger(__name__)

SOURCE_ROOMS_COUNT = 'roomsCount'
SOURCE_TOTAL_AREA = 'totalArea'
SOURCE_KITCHEN_AREA = 'kitchenArea'
SOURCE_IS_STUDIO = 'isStudio'
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
DEFAULT_ROOMS_COUNT = 1

SOURCE_CATEGORY_TO_CATEGORY: Dict[str, Category] = {
    'flatSale': Category.flat_sale,
    'newBuildingFlatSale': Category.new_building_flat_sale,
    'flatRent': Category.flat_rent,
}

GET_DISTRICTS_TYPE_TO_DISTRICT_TYPE = {
    GetDistrictsType.mikro_raion: DistrictType.mikroraion,
    GetDistrictsType.raion: DistrictType.raion,
    GetDistrictsType.okrug: DistrictType.okrug,
    GetDistrictsType.poselenie: DistrictType.poselenie
}


SOURCE_ID_TO_NAME_MAPPING = {
    '1': runtime_settings.AVITO_SOURCE_NAME,
    '8': runtime_settings.YANDEX_SOURCE_NAME,
    '13': runtime_settings.DOMCLICK_SOURCE_NAME,
}


CITY_LOCATION_ID = 1
REGION_LOCATION_ID = 2
SOURCE_AND_ID_DELIMETER = '_'
SOURCE_INDEX = 0


def extract_source_from_source_object_id(source_object_id: str) -> str:
    return source_object_id.split(SOURCE_AND_ID_DELIMETER)[SOURCE_INDEX]


def get_rooms_count_from_source_object_model(source_object_model: dict) -> int:
    rooms_count = source_object_model.get(SOURCE_ROOMS_COUNT)
    return rooms_count or DEFAULT_ROOMS_COUNT


def get_total_area_from_source_object_model(source_object_model: dict) -> Optional[float]:
    return source_object_model.get(SOURCE_TOTAL_AREA)


def get_kitchen_area_from_source_object_model(source_object_model: dict) -> Optional[float]:
    return source_object_model.get(SOURCE_KITCHEN_AREA)


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


def get_flat_type_from_source_object_model(source_object_model: dict) -> Optional[FlatType]:
    if source_object_model.get(SOURCE_IS_STUDIO):
        return FlatType.studio

    if source_object_model.get(SOURCE_ROOMS_COUNT) is None:
        return FlatType.open_plan

    return FlatType.rooms


def get_id_from_source_object_id(source_object_id: str) -> str:
    return source_object_id.split(sep='_')[1]


async def get_geo_by_source_object_model(source_object_model: dict) -> Optional[SwaggerGeo]:
    lng = get_lng_from_source_object_model(source_object_model)
    lat = get_lat_from_source_object_model(source_object_model)
    if not (lat and lng):
        statsd.incr('send-parsed-offers.create-object-model.geo.coordinates-missing')
        return None
    try:
        geocode_response = await v2_geocode(
            GeoCodedRequest(
                kind=DEFAULT_GEOCODE_KIND,
                lat=lat,
                lng=lng
            )
        )
    except ApiClientException:
        statsd.incr('send-parsed-offers.create-object-model.geo.geocode-failed')
        return None
    address = []
    house_location_id = None

    for detail in geocode_response.details:
        location_type_id = None
        _type = geo_type_to_type_mapping[detail.geo_type.value]

        if _type.is_location and detail.is_locality:
            location_type_id = CITY_LOCATION_ID

        if _type.is_location and not detail.is_locality:
            location_type_id = REGION_LOCATION_ID

        if _type.is_house:
            house_location_id = detail.id

        address.append(
            AddressInfo(
                id=detail.id,
                full_name=detail.full_name,
                short_name=detail.name,
                name=detail.name,
                type=_type,
                location_type_id=location_type_id,
                is_forming_address=True,
            )
        )

    if not house_location_id:
        statsd.incr('send-parsed-offers.create-object-model.geo.house-missing')
        return None

    districts = []
    district_parent_ids = []
    try:
        get_districts_response = await get_districts_by_house_id_cached(
            house_id=house_location_id
        )
        for district in get_districts_response:
            districts.append(
                DistrictInfo(
                    id=district.id,
                    location_id=district.location_id,
                    name=district.name,
                    parent_id=district.parent_id,
                    type=GET_DISTRICTS_TYPE_TO_DISTRICT_TYPE.get(district.type)
                )
            )
            if district.parent_id:
                district_parent_ids.append(district.parent_id)

        if district_parent_ids:
            get_districts_by_ids_response = await get_districts_by_district_ids_cached(
                ids=district_parent_ids
            )
            for district in get_districts_by_ids_response:
                districts.append(
                    DistrictInfo(
                        id=district.id,
                        location_id=district.location_id,
                        name=district.name,
                        parent_id=district.parent_id,
                        type=GET_DISTRICTS_TYPE_TO_DISTRICT_TYPE.get(district.type)
                    )
                )
    except GetDistrictsError:
        statsd.incr('send-parsed-offers.create-object-model.geo.get-districts-failed')
        return None

    undergrounds = []
    if geocode_response.details:
        undergrounds = await get_underground_by_coordinates(
            coordinates=Coordinates(
                lat=geocode_response.geo.lat,
                lng=geocode_response.geo.lng
            ),
            region_id=geocode_response.details[0].id
        )

    return SwaggerGeo(
        country_id=geocode_response.country_id,
        coordinates=Coordinates(
            lat=geocode_response.geo.lat,
            lng=geocode_response.geo.lng
        ),
        undergrounds=undergrounds,
        user_input=get_address_from_source_object_model(source_object_model),
        district=districts,
        address=address
    )


def get_phone_from_source_object_model(source_object_model: dict) -> Optional[str]:
    source_phones = source_object_model.get(SOURCE_PHONES)
    if not source_phones:
        return None

    return transform_phone_number_to_canonical_format(source_phones[0])


def create_source_model_from_parsed_offer(*, offer: ParsedOffer) -> SourceModel:
    source_id = extract_source_from_source_object_id(offer.source_object_id)

    return SourceModel(
        source=SOURCE_ID_TO_NAME_MAPPING.get(source_id, runtime_settings.AVITO_SOURCE_NAME),
        source_object_id=offer.source_object_id,
        timestamp=offer.timestamp,
        external_url=offer.source_object_model.get(SOURCE_URL)
    )


def offer_is_suitable(source_object_model: dict) -> bool:
    return source_object_model.get(SOURCE_CATEGORY) in settings.SUITABLE_CATEGORIES_FOR_REPORTING


async def create_object_model_from_parsed_offer(*, offer: ParsedOfferMessage) -> Optional[ObjectModel]:
    source_object_model = offer.source_object_model

    if not offer_is_suitable(source_object_model):
        return None

    phone_number = get_phone_from_source_object_model(source_object_model)
    if not phone_number:
        statsd.incr('send-parsed-offers.create-object-model.missing-phone')
        return None

    geo = await get_geo_by_source_object_model(source_object_model)
    if not geo:
        statsd.incr('send-parsed-offers.create-object-model.geo-failed')
        return None

    return ObjectModel(
            id=get_id_from_source_object_id(offer.source_object_id),
            bargain_terms=BargainTerms(
                price=get_price_from_source_object_model(source_object_model),
                currency=Currency.rur,
                utilities_terms=UtilitiesTerms(
                    included_in_price=True
                ),
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
            kitchen_area=get_kitchen_area_from_source_object_model(source_object_model),
            living_area=get_living_area_from_source_object_model(source_object_model),
            property_type=PropertyType.building,
            rooms_count=get_rooms_count_from_source_object_model(source_object_model),
            floor_number=get_floor_number_from_source_object_model(source_object_model),
            category=get_category_from_source_object_model(source_object_model),
            geo=geo,
            description=get_description_from_source_object_model(source_object_model),
            is_enabled_call_tracking=offer.is_calltracking,
            is_by_home_owner=get_is_by_homeowner_from_source_object_model(source_object_model),
            flat_type=get_flat_type_from_source_object_model(source_object_model),
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
