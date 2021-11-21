from cian_core.runtime_settings import runtime_settings

from external_offers.enums.object_model import Category


def get_mapping_offer_categories_to_priority(
    team_settings: dict
):
    SALE_PRIORITY = str(
        team_settings.get(
            'sale_priority',
            runtime_settings.SALE_PRIORITY
        )
    )
    RENT_PRIORITY = str(
        team_settings.get(
            'rent_priority',
            runtime_settings.RENT_PRIORITY
        )
    )
    FLAT_PRIORITY = str(
        team_settings.get(
            'flat_priority',
            runtime_settings.FLAT_PRIORITY
        )
    )
    SUBURBAN_PRIORITY = str(
        team_settings.get(
            'suburban_priority',
            runtime_settings.SUBURBAN_PRIORITY
        )
    )
    COMMERCIAL_PRIORITY = str(
        team_settings.get(
            'commercial_priority',
            runtime_settings.COMMERCIAL_PRIORITY
        )
    )

    RENT_FLAT_PRIORITY = RENT_PRIORITY + FLAT_PRIORITY
    RENT_COMMERCIAL_PRIORITY = RENT_PRIORITY + COMMERCIAL_PRIORITY
    RENT_SUBURBAN_PRIORITY = RENT_PRIORITY + SUBURBAN_PRIORITY
    SALE_FLAT_PRIORITY = SALE_PRIORITY + FLAT_PRIORITY
    SALE_COMMERCIAL_PRIORITY = SALE_PRIORITY + COMMERCIAL_PRIORITY
    SALE_SUBURBAN_PRIORITY = SALE_PRIORITY + SUBURBAN_PRIORITY

    return {
        Category.bed_rent: RENT_FLAT_PRIORITY,
        Category.building_rent: RENT_COMMERCIAL_PRIORITY,
        Category.building_sale: SALE_COMMERCIAL_PRIORITY,
        Category.business_rent: RENT_COMMERCIAL_PRIORITY,
        Category.business_sale: SALE_COMMERCIAL_PRIORITY,
        Category.car_service_rent: RENT_COMMERCIAL_PRIORITY,
        Category.car_service_sale: SALE_COMMERCIAL_PRIORITY,
        Category.commercial_land_rent: RENT_COMMERCIAL_PRIORITY,
        Category.commercial_land_sale: SALE_COMMERCIAL_PRIORITY,
        Category.cottage_rent: RENT_SUBURBAN_PRIORITY,
        Category.cottage_sale: SALE_SUBURBAN_PRIORITY,
        Category.daily_bed_rent: RENT_FLAT_PRIORITY,
        Category.daily_flat_rent: RENT_FLAT_PRIORITY,
        Category.daily_house_rent: RENT_FLAT_PRIORITY,
        Category.daily_room_rent: RENT_FLAT_PRIORITY,
        Category.domestic_services_rent: RENT_COMMERCIAL_PRIORITY,
        Category.domestic_services_sale: SALE_COMMERCIAL_PRIORITY,
        Category.flat_rent: RENT_FLAT_PRIORITY,
        Category.flat_sale: SALE_FLAT_PRIORITY,
        Category.flat_share_sale: SALE_FLAT_PRIORITY,
        Category.free_appointment_object_rent: RENT_COMMERCIAL_PRIORITY,
        Category.free_appointment_object_sale: SALE_COMMERCIAL_PRIORITY,
        Category.garage_rent: RENT_COMMERCIAL_PRIORITY,
        Category.garage_sale: SALE_COMMERCIAL_PRIORITY,
        Category.house_rent: RENT_SUBURBAN_PRIORITY,
        Category.house_sale: SALE_SUBURBAN_PRIORITY,
        Category.house_share_rent: RENT_SUBURBAN_PRIORITY,
        Category.house_share_sale: SALE_SUBURBAN_PRIORITY,
        Category.industry_rent: RENT_COMMERCIAL_PRIORITY,
        Category.industry_sale: SALE_COMMERCIAL_PRIORITY,
        Category.land_sale: SALE_SUBURBAN_PRIORITY,
        Category.new_building_flat_sale: SALE_FLAT_PRIORITY,
        Category.office_rent: RENT_COMMERCIAL_PRIORITY,
        Category.office_sale: SALE_COMMERCIAL_PRIORITY,
        Category.public_catering_rent: RENT_COMMERCIAL_PRIORITY,
        Category.public_catering_sale: SALE_COMMERCIAL_PRIORITY,
        Category.room_rent: RENT_FLAT_PRIORITY,
        Category.room_sale: SALE_FLAT_PRIORITY,
        Category.shopping_area_rent: RENT_COMMERCIAL_PRIORITY,
        Category.shopping_area_sale: SALE_COMMERCIAL_PRIORITY,
        Category.townhouse_rent: RENT_SUBURBAN_PRIORITY,
        Category.townhouse_sale: SALE_SUBURBAN_PRIORITY,
        Category.warehouse_rent: RENT_COMMERCIAL_PRIORITY,
        Category.warehouse_sale: SALE_COMMERCIAL_PRIORITY,
    }
