from typing import List, Optional

from my_offers.repositories.monolith_cian_announcementapi.entities import AddressInfo


def get_street_name(address: Optional[List[AddressInfo]]) -> Optional[str]:
    if not address:
        return None

    for item in address:
        if item.type and item.type.is_street and item.name:
            return item.name

    return None
