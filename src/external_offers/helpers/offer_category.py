from typing import Tuple

from external_offers.enums.object_model import Category, DealType, OfferType


CATEGORY_OFFER_TYPE_DEAL_TYPE = {
    # Продажа жилой
    Category.flat_sale: (OfferType.flat, DealType.sale),
    Category.room_sale: (OfferType.flat, DealType.sale),
    Category.new_building_flat_sale: (OfferType.flat, DealType.sale),
    Category.flat_share_sale: (OfferType.flat, DealType.sale),

    # Продажа загородной
    Category.house_sale: (OfferType.suburban, DealType.sale),
    Category.cottage_sale: (OfferType.suburban, DealType.sale),
    Category.townhouse_sale: (OfferType.suburban, DealType.sale),
    Category.house_share_sale: (OfferType.suburban, DealType.sale),
    Category.land_sale: (OfferType.suburban, DealType.sale),

    # Аренда жилой
    Category.flat_rent: (OfferType.flat, DealType.rent),
    Category.room_rent: (OfferType.flat, DealType.rent),
    Category.bed_rent: (OfferType.flat, DealType.rent),

    # Аренда загородной
    Category.house_rent: (OfferType.suburban, DealType.rent),
    Category.cottage_rent: (OfferType.suburban, DealType.rent),
    Category.townhouse_rent: (OfferType.suburban, DealType.rent),
    Category.house_share_rent: (OfferType.suburban, DealType.rent),

    # Аренда посуточной
    Category.daily_flat_rent: (OfferType.flat, DealType.rent),
    Category.daily_room_rent: (OfferType.flat, DealType.rent),
    Category.daily_bed_rent: (OfferType.flat, DealType.rent),
    Category.daily_house_rent: (OfferType.suburban, DealType.rent),

    # Продажа коммерческой
    Category.office_sale: (OfferType.commercial, DealType.sale),
    Category.warehouse_sale: (OfferType.commercial, DealType.sale),
    Category.shopping_area_sale: (OfferType.commercial, DealType.sale),
    Category.industry_sale: (OfferType.commercial, DealType.sale),
    Category.building_sale: (OfferType.commercial, DealType.sale),
    Category.free_appointment_object_sale: (OfferType.commercial, DealType.sale),
    Category.business_sale: (OfferType.commercial, DealType.sale),
    Category.commercial_land_sale: (OfferType.commercial, DealType.sale),
    Category.garage_sale: (OfferType.commercial, DealType.sale),
    Category.public_catering_sale: (OfferType.commercial, DealType.sale),
    Category.car_service_sale: (OfferType.commercial, DealType.sale),
    Category.domestic_services_sale: (OfferType.commercial, DealType.sale),

    # Аренда коммерческой
    Category.office_rent: (OfferType.commercial, DealType.rent),
    Category.warehouse_rent: (OfferType.commercial, DealType.rent),
    Category.shopping_area_rent: (OfferType.commercial, DealType.rent),
    Category.industry_rent: (OfferType.commercial, DealType.rent),
    Category.building_rent: (OfferType.commercial, DealType.rent),
    Category.free_appointment_object_rent: (OfferType.commercial, DealType.rent),
    Category.business_rent: (OfferType.commercial, DealType.rent),
    Category.commercial_land_rent: (OfferType.commercial, DealType.rent),
    Category.garage_rent: (OfferType.commercial, DealType.rent),
    Category.public_catering_rent: (OfferType.commercial, DealType.rent),
    Category.car_service_rent: (OfferType.commercial, DealType.rent),
    Category.domestic_services_rent: (OfferType.commercial, DealType.rent),
}


def get_types(category: Category) -> Tuple[OfferType, DealType]:
    return CATEGORY_OFFER_TYPE_DEAL_TYPE[category]
