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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_daily_term_rent is True


@pytest.mark.parametrize('category', [
    Category.house_sale,
    Category.cottage_sale,
    Category.land_sale,
    Category.townhouse_sale,
])
def test_parsed_offer__is_suburban_sale(category):
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
        floor_number=1,
        floors_count=2,
        rooms_count=4,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_suburban_sale is True


@pytest.mark.parametrize('category, expected', [
    (Category.house_sale, False),
    (Category.land_sale, True),
])
def test_parsed_offer__is_land_sale(category, expected):
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
        floor_number=1,
        floors_count=2,
        rooms_count=4,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_land is expected


def test_parsed_offer__house_sale__has_land_area():
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=Category.house_sale,
        region=4607,
        title='Дом 230 м² на участке 6 сот.',
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
    assert offer.land_area == 6.0


def test_parsed_offer__land_sale__has_land_area():
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=Category.land_sale,
        region=4607,
        title='Участок 6 сот.',
        description='blah blah blah blah blah blah blah blah blah blah blah blah',
        address='Рязанская область, Рязань, Касимовское ш., 56к1',
        price=100_000,
        pricetype=1,
        town='Рязань',
        contact='Пушкин Птурович',
        total_area=0,
        floor_number=0,
        floors_count=0,
        rooms_count=0,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.land_area == 6.0


def test_parsed_offer__land_sale__has_no_land_area():
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=Category.land_sale,
        region=4607,
        title='Участок',
        description='blah blah blah blah blah blah blah blah blah blah blah blah',
        address='Рязанская область, Рязань, Касимовское ш., 56к1',
        price=100_000,
        pricetype=1,
        town='Рязань',
        contact='Пушкин Птурович',
        total_area=0,
        floor_number=0,
        floors_count=0,
        rooms_count=0,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.land_area is None


@pytest.mark.parametrize('value, expected', [
    ('6.2', 6.2), ('6', 6.0), ('14.2', 14.2)
])
def test_parsed_offer__land_sale__has_land_area__float(value, expected):
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=Category.land_sale,
        region=4607,
        title=f'Участок {value} сот.',
        description='blah blah blah blah blah blah blah blah blah blah blah blah',
        address='Рязанская область, Рязань, Касимовское ш., 56к1',
        price=100_000,
        pricetype=1,
        town='Рязань',
        contact='Пушкин Птурович',
        total_area=0,
        floor_number=0,
        floors_count=0,
        rooms_count=0,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.land_area == expected


@pytest.mark.parametrize('value, expected', [
    ('6.2', 6.2), ('6', 6.0), ('14.2', 14.2)
])
def test_parsed_offer__house_sale__has_land_area__float(value, expected):
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=Category.house_sale,
        region=4607,
        title=f'Дом 230 м² на участке {value} сот.',
        description='blah blah blah blah blah blah blah blah blah blah blah blah',
        address='Рязанская область, Рязань, Касимовское ш., 56к1',
        price=100_000,
        pricetype=1,
        town='Рязань',
        contact='Пушкин Птурович',
        total_area=0,
        floor_number=0,
        floors_count=0,
        rooms_count=0,
        is_studio=False,
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.land_area == expected


@pytest.mark.parametrize('category, expected', [
    (Category.house_sale, None),
    (Category.cottage_sale, None),
    (Category.townhouse_sale, None),
    (Category.land_sale, 'ИЖС'),
])
def test_parsed_offer__has_land_status(category, expected):
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=category,
        region=4607,
        title='Дом 230 кв на участке 6 сот. (ИЖС)',
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.land_status == expected


def test_parsed_offer__has_no_land_status():
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=Category.land_sale,
        region=4607,
        title='Участок',
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.land_status is None


@pytest.mark.parametrize('unit, expected', [
    ('га.', 'hectare'),
    ('сот.', 'sotka'),
    (None, None),
])
def test_parsed_offer__area_unit_type(unit, expected):
    # arrange
    offer = ParsedObjectModel(
        phones=['89307830154'],
        category=Category.land_sale,
        region=4607,
        title=f'Дом 230 кв на участке 6 {unit}',
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.land_area_unit == expected


@pytest.mark.parametrize('category', [
    Category.office_sale,
    Category.free_appointment_object_sale,
    Category.shopping_area_sale,
    Category.warehouse_sale,
    Category.industry_sale,
    Category.building_sale,
    Category.business_sale,
    Category.commercial_land_sale,
    Category.office_rent,
    Category.free_appointment_object_rent,
    Category.shopping_area_rent,
    Category.warehouse_rent,
    Category.industry_rent,
    Category.building_rent,
    Category.business_rent,
    Category.commercial_land_rent,
])
def test_parsed_offer__is_commercial_type(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_commercial_type is True


@pytest.mark.parametrize('category', [
    Category.office_sale,
    Category.free_appointment_object_sale,
    Category.shopping_area_sale,
    Category.warehouse_sale,
    Category.industry_sale,
    Category.building_sale,
    Category.business_sale,
    Category.commercial_land_sale,
])
def test_parsed_offer__is_commercial_sale(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_commercial_sale is True


@pytest.mark.parametrize('category', [
    Category.office_rent,
    Category.free_appointment_object_rent,
    Category.shopping_area_rent,
    Category.warehouse_rent,
    Category.industry_rent,
    Category.building_rent,
    Category.business_rent,
    Category.commercial_land_rent,
])
def test_parsed_offer__is_commercial_rent(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_commercial_rent is True


@pytest.mark.parametrize('category', [
    Category.office_rent,
    Category.office_sale,
])
def test_parsed_offer__is_office(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_office is True


@pytest.mark.parametrize('category', [
    Category.free_appointment_object_rent,
    Category.free_appointment_object_sale,
])
def test_parsed_offer__is_free_appointment_object(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_free_appointment_object is True


@pytest.mark.parametrize('category', [
    Category.shopping_area_rent,
    Category.shopping_area_sale,
])
def test_parsed_offer__is_shopping_area(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_shopping_area is True


@pytest.mark.parametrize('category', [
    Category.warehouse_rent,
    Category.warehouse_sale,
])
def test_parsed_offer__is_warehouse(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_warehouse is True


@pytest.mark.parametrize('category', [
    Category.industry_rent,
    Category.industry_sale,
])
def test_parsed_offer__is_industry(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_industry is True


@pytest.mark.parametrize('category', [
    Category.building_rent,
    Category.building_sale,
])
def test_parsed_offer__is_building(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_building is True


@pytest.mark.parametrize('category', [
    Category.business_rent,
    Category.business_sale,
])
def test_parsed_offer__is_business(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_business is True


@pytest.mark.parametrize('category', [
    Category.business_sale,
])
def test_parsed_offer__is_business_sale(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_business_sale is True


@pytest.mark.parametrize('category', [
    Category.commercial_land_rent,
    Category.commercial_land_sale,
])
def test_parsed_offer__is_commercial_land(category):
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
        url='https://www.cian.ru/rent/commercial/225540774/'
    )

    # act
    # assert
    assert offer.is_commercial_land is True
