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


@pytest.mark.parametrize('category', [
    Category.flat_rent,
    Category.flat_sale,
    Category.flat_share_sale,
    Category.daily_flat_rent,
])
def test_parsed_offer__is_flat(category):
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
    assert offer.is_flat is True


@pytest.mark.parametrize('category', [
    Category.room_rent,
    Category.room_sale,
    Category.daily_room_rent,
])
def test_parsed_offer__is_room(category):
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
    assert offer.is_room is True


@pytest.mark.parametrize('category', [
    Category.flat_share_sale,
])
def test_parsed_offer__is_share(category):
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
    assert offer.is_share is True


@pytest.mark.parametrize('category', [
    Category.bed_rent,
    Category.daily_bed_rent,
])
def test_parsed_offer__is_bed(category):
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
    assert offer.is_bed is True


@pytest.mark.parametrize('category', [
    Category.flat_rent,
    Category.room_rent,
    Category.bed_rent
])
def test_parsed_offer__is_long_term_rent(category):
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
    assert offer.is_long_term_rent is True


@pytest.mark.parametrize('category', [
    Category.daily_bed_rent,
    Category.daily_flat_rent,
    Category.daily_room_rent
])
def test_parsed_offer__is_daily_term_rent(category):
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
    assert offer.is_daily_term_rent is True


@pytest.mark.parametrize('category', [
    Category.house_sale,
    Category.cottage_sale,
    Category.land_sale,
])
def test_parsed_offer__is_suburban(category):
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=category,
        region=4607,
        title='Дом',
        description='blah blah blah blah blah blah blah blah blah blah blah blah',
        address='Рязанская область, Рязань, Касимовское ш., 56к1',
        price=100_000,
        pricetype=1,
        town='Рязань',
        contact='Пушкин Птурович',
        total_area=120,
        land_area=4,
        floor_number=1,
        floors_count=2,
        rooms_count=4,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/')

    # act
    # assert
    assert offer.is_suburban is True
