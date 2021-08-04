from my_offers.repositories.monolith_cian_announcementapi.entities.bargain_terms import PriceType
from my_offers.repositories.monolith_cian_announcementapi.entities.land import AreaUnitType


def area_to_meters_kf(unit_type: AreaUnitType) -> int:
    return 100 if unit_type.is_sotka else 10000


def price_type_to_meters_kf(price_type: PriceType) -> int:
    if price_type.is_hectare:
        return 10000
    if price_type.is_sotka:
        return 100

    return 1
