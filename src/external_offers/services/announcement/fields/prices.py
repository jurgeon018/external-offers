from typing import Optional, Tuple

from my_offers.repositories.monolith_cian_announcementapi.entities import BargainTerms
from my_offers.services.announcement.helpers.units import price_type_to_meters_kf


def get_prices(
        *,
        bargain_terms: BargainTerms,
        total_area: Optional[float] = None
) -> Tuple[Optional[float], Optional[float]]:
    price: Optional[float] = None
    price_per_meter: Optional[float] = None

    price_type = bargain_terms.price_type
    if not price_type:
        return price, price_per_meter

    if bargain_terms.price:
        if price_type.is_all:
            price = bargain_terms.price

            if total_area and price:
                price_per_meter = round(price / total_area, 2)

        else:
            kf = price_type_to_meters_kf(price_type)
            price_per_meter = (
                round(bargain_terms.price / kf, 2)
                if bargain_terms.price
                else None
            )

            if total_area and price_per_meter:
                price = price_per_meter * total_area

    return price, price_per_meter
