from typing import Optional

from cian_enum import StrEnum


class ExternalOfferType(StrEnum):
    commercial = 'commercial'
    """Коммерческая"""

    @classmethod
    def from_str(cls, value: Optional[str]):
        return {
            'commercial': cls.commercial,
    }[value] if value else None
