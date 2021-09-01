from enum import Enum
from typing import TypeVar, Optional

from cian_entities import EntityMapper
from cian_entities.mappers import IntEnumMapper, Mapper, ValueMapper

from external_offers.entities.parsed_offers import ParsedOffer, ParsedOfferForCreation, ParsedOfferMessage
from external_offers.enums.external_offer_type import ExternalOfferType

TEnum = TypeVar('TEnum', bound=Enum)


class StrToExternalOfferTypeValueMapper(Mapper[str, int]):
    def map_to(self, obj):
        raise NotImplementedError()

    def map_from(self, data: Optional[str]) -> int:
        if data is None:
            return ExternalOfferType.Default.value

        if data == 'commercial':
            return ExternalOfferType.Commercial.value

        raise ValueError(f'Not supported data for ExternalOfferType: {data}')


str_to_external_offer_type_value_mapper = StrToExternalOfferTypeValueMapper()


parsed_offer_message_mapper = EntityMapper(
    ParsedOfferMessage,
    without_camelcase=True,
    mappers={
        'timestamp': ValueMapper(),
        'external_offer_type': str_to_external_offer_type_value_mapper
    }
)

parsed_offer_mapper = EntityMapper(
    ParsedOffer,
    without_camelcase=True,
    mappers={
        'timestamp': ValueMapper(),
        'created_at': ValueMapper(),
        'updated_at': ValueMapper(),
        'external_offer_type': IntEnumMapper(),
    }
)

parsed_offer_for_creation_mapper = EntityMapper(
    ParsedOfferForCreation,
    without_camelcase=True,
    mappers={
        'timestamp': ValueMapper(),
    }
)
