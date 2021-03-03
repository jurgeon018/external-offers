from typing import Dict

from external_offers.repositories.monolith_cian_announcementapi.entities.address_info import Type
from external_offers.repositories.monolith_cian_announcementapi.entities.bargain_terms import SaleType
from external_offers.repositories.monolith_cian_announcementapi.entities.details import GeoType
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import FlatType


geo_type_value_to_type_mapping: Dict[GeoType, Type] = {
    GeoType.house.value: Type.house,
    GeoType.country.value: Type.country,
    GeoType.district.value: Type.district,
    GeoType.road.value: Type.road,
    GeoType.street.value: Type.street,
    GeoType.underground.value: Type.underground,
    GeoType.location.value: Type.location
}

segment_to_homeowner_mapping: Dict[str, bool] = {
    'a': False,
    'b': False,
    'c': False,
    'd': True
}

save_offer_sale_type_to_sale_type_mapping: Dict[str, SaleType] = {
    'free': SaleType.free,
    'alternative': SaleType.alternative
}

save_offer_realty_type_to_is_apartments_mapping: Dict[str, bool] = {
    'apartments': True,
    'flat': False
}

save_offer_rooms_count_to_flat_type_mapping: Dict[str, FlatType] = {
    'room1': FlatType.rooms,
    'room2': FlatType.rooms,
    'room3': FlatType.rooms,
    'room4': FlatType.rooms,
    'room5': FlatType.rooms,
    'room6_plus': FlatType.rooms,
    'open_plan': FlatType.open_plan,
    'studio': FlatType.studio
}

save_offer_rooms_count_to_num_mapping: Dict[str, int] = {
    'room1': 1,
    'room2': 2,
    'room3': 3,
    'room4': 4,
    'room5': 5,
    'room6_plus': 6,
    'open_plan': 1,
    'studio': 1
}
