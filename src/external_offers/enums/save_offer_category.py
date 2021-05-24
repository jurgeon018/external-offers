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
