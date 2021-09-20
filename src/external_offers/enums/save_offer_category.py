from cian_enum import StrEnum


class SaveOfferCategory(StrEnum):
    share = 'share'
    """Доля в квартире"""
    flat = 'flat'
    """Квартира"""
    room = 'room'
    """Комната"""
    bed = 'bed'
    """Койко-место"""
    house = 'house'
    """Дом"""
    cottage = 'cottage'
    """Коттедж"""
    townhouse = 'townhouse'
    """Таунхаус"""
    land = 'land'
    """Участок"""
    office = 'office'
    """Офис"""
    free_appointment_object = 'freeAppointmentObject'
    """Помещение свободного назначения"""
    shopping_area = 'shoppingArea'
    """Торговая площадь"""
    warehouse = 'warehouse'
    """Склад"""
    industry = 'industry'
    """Производство"""
    building = 'building'
    """здание"""
    business = 'business'
    """Готовый бизнес"""
    commercial_land = 'commercialLand'
    """Коммерческая земля"""
