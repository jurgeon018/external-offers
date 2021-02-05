from cian_enum import StrEnum


class SaveOfferTerm(StrEnum):
    long_term = 'long'
    """Долгосрочная"""
    daily_term = 'daily'
    """Посуточная"""
