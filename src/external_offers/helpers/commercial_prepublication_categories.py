from external_offers.enums.object_model import Category


# Все коммерческие категории, кроме гаража
COMMERCIAL_PREPUBLICATION_CATEGORIES = [
    Category.office_sale.value,
    Category.warehouse_sale.value,
    Category.shopping_area_sale.value,
    Category.industry_sale.value,
    Category.building_sale.value,
    Category.free_appointment_object_sale.value,
    Category.business_sale.value,
    Category.commercial_land_sale.value,
    Category.public_catering_sale.value,
    Category.car_service_sale.value,
    Category.domestic_services_sale.value,
    Category.office_rent.value,
    Category.warehouse_rent.value,
    Category.shopping_area_rent.value,
    Category.industry_rent.value,
    Category.building_rent.value,
    Category.free_appointment_object_rent.value,
    Category.business_rent.value,
    Category.commercial_land_rent.value,
    Category.public_catering_rent.value,
    Category.car_service_rent.value,
    Category.domestic_services_rent.value,
]
