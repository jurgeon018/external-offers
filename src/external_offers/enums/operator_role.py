from cian_enum import NoFormat, StrEnum


class OperatorRole(StrEnum):
    __value_format__ = NoFormat

    commercial_prepublication_moderator = 'CommercialPrepublicationModerator'
    """Модератор предпубликации коммерческих объявлений"""
