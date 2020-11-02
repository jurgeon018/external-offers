from external_offers.entities.parsed_offers import ParsedObjectModel, ParsedOffer
from external_offers.repositories import postgresql


async def save_parsed_offer(*, offer: ParsedOffer) -> None:
    """ Сохранить объявление с внешней площадки. """

    await postgresql.save_parsed_offer(parsed_offer=offer)


async def get_parsed_offer(parsed_offer_id: str) -> ParsedObjectModel:
    return ParsedObjectModel(
        phones=['89134488338', '+7-965-448-77-02'],
        category='flatSale',
        address='ул. просторная 6, квартира 200',
        title='2-к квартира, 65.4 м², 5/10 эт.',
        contact='Пушкин Александрочвич',
        description='Квартира 10 из 10',
        floor_number=5,
        floors_count=10,
        total_area=60,
        price=1_000_000,
        pricetype=1,
        rooms_count=3,
        region=1,
        url='https://www.cian.ru/sale/commercial/152624841/'
    )
