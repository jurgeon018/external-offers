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
