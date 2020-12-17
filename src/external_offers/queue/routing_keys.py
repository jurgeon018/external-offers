from cian_enum import StrEnum


class ExternalOffersV1RoutingKey(StrEnum):
    changed = 'external-offers.offers-reporting.v1.changed'
    """Событие изменения объявления"""
    deleted = 'external-offers.offers-reporting.v1.deleted'
    """Событие удаления объявления"""
