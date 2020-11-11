from cian_enum import NoFormat, StrEnum


class DealType(StrEnum):
    """Тип сделки"""
    rent = 'rent'
    """Аренда"""
    sale = 'sale'
    """Продажа"""


class OfferType(StrEnum):
    """Тип недвижимости"""
    flat = 'flat'
    """Жилая"""
    newobject = 'newobject'
    """Новостройки"""
    suburban = 'suburban'
    """Загородная"""
    commercial = 'commercial'
    """Коммерческая"""


class Category(StrEnum):
    __value_format__ = NoFormat
    bed_rent = 'bedRent'
    """Койко-место"""
    building_rent = 'buildingRent'
    """Здание"""
    building_sale = 'buildingSale'
    """Здание"""
    business_rent = 'businessRent'
    """Готовый бизнес"""
    business_sale = 'businessSale'
    """Готовый бизнес"""
    car_service_rent = 'carServiceRent'
    """Аренда автосервис"""
    car_service_sale = 'carServiceSale'
    """Продажа автосервиса"""
    commercial_land_rent = 'commercialLandRent'
    """Коммерческая земля"""
    commercial_land_sale = 'commercialLandSale'
    """Коммерческая земля"""
    cottage_rent = 'cottageRent'
    """Коттедж"""
    cottage_sale = 'cottageSale'
    """Коттедж"""
    daily_bed_rent = 'dailyBedRent'
    """Посуточная аренда койко-места"""
    daily_flat_rent = 'dailyFlatRent'
    """Посуточная аренда квартиры"""
    daily_house_rent = 'dailyHouseRent'
    """Посуточная аренда дома, дачи, коттеджа"""
    daily_room_rent = 'dailyRoomRent'
    """Посуточная аренда комнаты"""
    domestic_services_rent = 'domesticServicesRent'
    """Аренда помещения под бытовые услуги"""
    domestic_services_sale = 'domesticServicesSale'
    """Продажа помещения под бытовые услуги"""
    flat_rent = 'flatRent'
    """Квартира"""
    flat_sale = 'flatSale'
    """Квартира"""
    flat_share_sale = 'flatShareSale'
    """Доля в квартире"""
    free_appointment_object_rent = 'freeAppointmentObjectRent'
    """Помещение свободного назначения"""
    free_appointment_object_sale = 'freeAppointmentObjectSale'
    """Помещение свободного назначения"""
    garage_rent = 'garageRent'
    """Гараж"""
    garage_sale = 'garageSale'
    """Гараж"""
    house_rent = 'houseRent'
    """Дом/дача"""
    house_sale = 'houseSale'
    """Дом/дача"""
    house_share_rent = 'houseShareRent'
    """Часть дома"""
    house_share_sale = 'houseShareSale'
    """Часть дома"""
    industry_rent = 'industryRent'
    """Производство"""
    industry_sale = 'industrySale'
    """Производство"""
    land_sale = 'landSale'
    """Участок"""
    new_building_flat_sale = 'newBuildingFlatSale'
    """Квартира в новостройке"""
    office_rent = 'officeRent'
    """Офис"""
    office_sale = 'officeSale'
    """Офис"""
    public_catering_rent = 'publicCateringRent'
    """Аренда общепита"""
    public_catering_sale = 'publicCateringSale'
    """Продажа общепита"""
    room_rent = 'roomRent'
    """Комната"""
    room_sale = 'roomSale'
    """Комната"""
    shopping_area_rent = 'shoppingAreaRent'
    """Торговая площадь"""
    shopping_area_sale = 'shoppingAreaSale'
    """Торговая площадь"""
    townhouse_rent = 'townhouseRent'
    """Таунхаус"""
    townhouse_sale = 'townhouseSale'
    """Таунхаус"""
    warehouse_rent = 'warehouseRent'
    """Склад"""
    warehouse_sale = 'warehouseSale'
    """Склад"""
