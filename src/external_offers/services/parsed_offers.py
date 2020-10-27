from external_offers.entities.parsed_offers import ParsedOffer
from external_offers.repositories import postgresql


async def save_parsed_offer(*, offer: ParsedOffer) -> None:
    """ Сохранить объявление с внешней площадки. """

    await postgresql.save_parsed_offer(parsed_offer=offer)
