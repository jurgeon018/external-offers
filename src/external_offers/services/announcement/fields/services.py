from typing import List, Optional

from my_offers import enums
from my_offers.repositories.monolith_cian_announcementapi.entities import PublishTerms
from my_offers.repositories.monolith_cian_announcementapi.entities.publish_term import Services


OFFER_SERVICES_MAP = {
    Services.auction: enums.OfferServices.auction,
    Services.free: enums.OfferServices.free,
    Services.paid: enums.OfferServices.paid,
    Services.premium: enums.OfferServices.premium,
    Services.top3: enums.OfferServices.top3,
}


def get_services(publish_terms: Optional[PublishTerms]) -> List[enums.OfferServices]:
    result: List[enums.OfferServices] = []
    if not publish_terms:
        return result

    if not publish_terms.terms:
        return result

    has_highlight = False
    for term in publish_terms.terms:
        if not term.services:
            continue
        for service in term.services:
            if offer_service := OFFER_SERVICES_MAP.get(service):
                result.append(offer_service)

            has_highlight = has_highlight or service.is_highlight

    if has_highlight and enums.OfferServices.premium in result:
        result.append(enums.OfferServices.premium_highlight)

    return result
