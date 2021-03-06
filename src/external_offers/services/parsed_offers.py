from typing import Optional

from external_offers.entities.parsed_offers import ParsedOfferDiff, ParsedOfferMessage
from external_offers.repositories import postgresql


SOURCE_AND_ID_DELIMETER = '_'
SOURCE_INDEX = 0

def extract_source_from_source_object_id(source_object_id: str) -> str:
    return source_object_id.split(SOURCE_AND_ID_DELIMETER)[SOURCE_INDEX]


async def save_parsed_offer(*, offer: ParsedOfferMessage) -> Optional[ParsedOfferDiff]:
    """ Сохранить объявление с внешней площадки. """
    return await postgresql.save_parsed_offer(parsed_offer=offer)
