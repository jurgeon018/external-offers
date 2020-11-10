import pytest

from external_offers.entities.parsed_offers import ParsedObjectModel
from external_offers.enums.object_model import Category


@pytest.mark.parametrize('category', [
    Category.flat_sale,
    Category.room_sale,
    Category.flat_share_sale,
])
def test_parsed_offer__is_flat_sale(category):
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=category,
        region=4607,
        title='2-к квартира, 55 м², 4/9 эт.',
        description='blah blah blah blah blah blah blah blah blah blah blah blah',
        address='Рязанская область, Рязань, Касимовское ш., 56к1',
        price=100_000,
        pricetype=1,
        town='Рязань',
        contact='Пушкин Птурович',
        total_area=120,
        floor_number=1,
        floors_count=2,
        rooms_count=4,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/')

    # act
    # assert
    assert offer.is_sale is True


@pytest.mark.parametrize('category', [
    Category.room_rent,
    Category.flat_rent,
    Category.bed_rent,
])
def test_parsed_offer__is_flat_rent(category):
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=category,
        region=4607,
        title='2-к квартира, 55 м², 4/9 эт.',
        description='blah blah blah blah blah blah blah blah blah blah blah blah',
        address='Рязанская область, Рязань, Касимовское ш., 56к1',
        price=100_000,
        pricetype=1,
        town='Рязань',
        contact='Пушкин Птурович',
        total_area=120,
        floor_number=1,
        floors_count=2,
        rooms_count=4,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/')

    # act
    # assert
    assert offer.is_rent is True


@pytest.mark.parametrize('category', [
    Category.flat_rent,
    Category.flat_sale,
    Category.flat_share_sale,
])
def test_parsed_offer__is_allow_rooms(category):
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=category,
        region=4607,
        title='2-к квартира, 55 м², 4/9 эт.',
        description='blah blah blah blah blah blah blah blah blah blah blah blah',
        address='Рязанская область, Рязань, Касимовское ш., 56к1',
        price=100_000,
        pricetype=1,
        town='Рязань',
        contact='Пушкин Птурович',
        total_area=120,
        floor_number=1,
        floors_count=2,
        rooms_count=4,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/')

    # act
    # assert
    assert offer.is_allow_rooms is True


@pytest.mark.parametrize('category', [
    Category.flat_rent,
    Category.flat_sale,
    Category.flat_share_sale,
    Category.room_rent,
    Category.room_sale,
])
def test_parsed_offer__is_allow_realty_type(category):
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=category,
        region=4607,
        title='2-к квартира, 55 м², 4/9 эт.',
        description='blah blah blah blah blah blah blah blah blah blah blah blah',
        address='Рязанская область, Рязань, Касимовское ш., 56к1',
        price=100_000,
        pricetype=1,
        town='Рязань',
        contact='Пушкин Птурович',
        total_area=120,
        floor_number=1,
        floors_count=2,
        rooms_count=4,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/')

    # act
    # assert
    assert offer.is_allow_realty_type is True
