from cian_http.exceptions import ApiClientException
from cian_test_utils import future

from external_offers.entities.parsed_offers import ParsedOfferMessage
from external_offers.repositories.monolith_cian_geoapi.entities import Details, GeoCodedResponse
from external_offers.repositories.monolith_cian_geoapi.entities.details import GeoType
from external_offers.services.parsed_offers import (
    DEFAULT_ROOMS_COUNT,
    FlatType,
    create_object_model_from_parsed_offer,
    get_flat_type_from_source_object_model,
    get_geo_by_source_object_model,
    get_rooms_count_from_source_object_model,
    send_parsed_offer_change_event,
)


def test_get_rooms_count__rooms_null__return_deafult():
    # arrange
    source_object_model = {
        'roomsCount': None
    }

    # act
    result = get_rooms_count_from_source_object_model(source_object_model)

    # assert
    assert result == DEFAULT_ROOMS_COUNT


def test_get_flat_type__is_studio__return_studio_type():
    # arrange
    source_object_model = {
        'isStudio': True,
        'roomsCount': None,
    }

    # act
    result = get_flat_type_from_source_object_model(source_object_model)

    # assert
    assert result == FlatType.studio


def test_get_flat_type__not_stuido_and_no_rooms_return_open_plan_type():
    # arrange
    source_object_model = {
        'isStudio': None,
        'roomsCount': None,
    }

    # act
    result = get_flat_type_from_source_object_model(source_object_model)

    # assert
    assert result == FlatType.open_plan


async def test_send_parsed_offer_change_event__not_suitable_category__returns_without_call(
    mocker,
    fake_settings
):
    # arrange
    message = mocker.MagicMock(
        spec=ParsedOfferMessage
    )
    message.source_object_model = {
        'category': 'flatSale'
    }

    await fake_settings.set(
        SUITABLE_CATEGORIES_FOR_REPORTING=[]
    )
    get_phones_mock = mocker.patch('external_offers.services.parsed_offers.get_phone_from_source_object_model')

    # act
    await send_parsed_offer_change_event(
        offer=message
    )

    # assert
    assert not get_phones_mock.called


async def test_send_parsed_offer_change_event__no_phones__returns_without_call(
    mocker,
    fake_settings
):
    # arrange
    message = mocker.MagicMock(
        spec=ParsedOfferMessage
    )
    message.source_object_model = {
        'category': 'flatSale',
        'phones': []
    }

    await fake_settings.set(
        SUITABLE_CATEGORIES_FOR_REPORTING=['flatSale']
    )
    get_geo_mock = mocker.patch('external_offers.services.parsed_offers.get_geo_by_source_object_model')

    # act
    await send_parsed_offer_change_event(
        offer=message
    )

    # assert
    assert not get_geo_mock.called


async def test_send_parsed_offer_change_event__no_lat__returns_without_call(
    mocker,
):
    # arrange
    source_object_model = {
        'lng': 1,
        'lat': None
    }

    geocode_mock = mocker.patch(
        'external_offers.services.parsed_offers.v2_geocode'
    )

    # act
    result = await get_geo_by_source_object_model(
        source_object_model
    )

    # assert
    assert not geocode_mock.called
    assert not result


async def test_send_parsed_offer_change_event__no_lng__returns_without_call(
    mocker,
):
    # arrange
    source_object_model = {
        'lng': None,
        'lat': 1
    }

    geocode_mock = mocker.patch(
        'external_offers.services.parsed_offers.v2_geocode'
    )

    # act
    result = await get_geo_by_source_object_model(
        source_object_model
    )

    # assert
    assert not geocode_mock.called
    assert not result


async def test_send_parsed_offer_change_event__lng_and_lat_exist__returns_with_call(
    mocker,
):
    # arrange
    source_object_model = {
        'lng': 1,
        'lat': 1
    }

    geocode_mock = mocker.patch(
        'external_offers.services.parsed_offers.v2_geocode',
        side_effect=ApiClientException('Error')
    )

    # act
    result = await get_geo_by_source_object_model(
        source_object_model
    )

    # assert
    assert geocode_mock.called
    assert not result


async def test_send_parsed_offer_change_event__no_house_in_geocode_response__returns_none(
    mocker,
):
    # arrange
    source_object_model = {
        'lng': 1,
        'lat': 1
    }

    geocode_mock = mocker.patch(
        'external_offers.services.parsed_offers.v2_geocode',
        return_value=future(
            GeoCodedResponse(
                details=[
                    Details(
                        id=1,
                        full_name='Свердловская область',
                        name='область',
                        geo_type=GeoType.location,
                    )
                ]
            )
        )
    )
    v1_get_districts_mock = mocker.patch(
        'external_offers.services.parsed_offers.v1_get_districts_by_child',
    )

    # act
    result = await get_geo_by_source_object_model(
        source_object_model
    )

    # assert
    assert geocode_mock.called
    assert not v1_get_districts_mock.called
    assert not result


async def test_send_parsed_offer_change_event__get_district_failed__returns_none(
    mocker,
):
    # arrange
    source_object_model = {
        'lng': 1,
        'lat': 1
    }

    geocode_mock = mocker.patch(
        'external_offers.services.parsed_offers.v2_geocode',
        return_value=future(
            GeoCodedResponse(
                details=[
                    Details(
                        id=1,
                        full_name='25',
                        name='25',
                        geo_type=GeoType.house,
                    )
                ]
            )
        )
    )

    v1_get_districts_mock = mocker.patch(
        'external_offers.services.parsed_offers.v1_get_districts_by_child',
        side_effect=ApiClientException('Error')
    )

    get_undergrounds_mock = mocker.patch(
        'external_offers.services.parsed_offers.get_underground_by_coordinates'
    )

    # act
    result = await get_geo_by_source_object_model(
        source_object_model
    )

    # assert
    assert geocode_mock.called
    assert v1_get_districts_mock.called
    assert not get_undergrounds_mock.called
    assert not result


async def test_create_object_model_from_parsed__returned_no_geo__returns_none(
    mocker,
    fake_settings
):
    # arrange
    message = mocker.MagicMock(
        spec=ParsedOfferMessage
    )
    message.source_object_model = {
        'category': 'flatSale',
        'phones': ['+798195412324']
    }

    await fake_settings.set(
        SUITABLE_CATEGORIES_FOR_REPORTING=['flatSale']
    )

    get_geo_mock = mocker.patch(
        'external_offers.services.parsed_offers.get_geo_by_source_object_model',
        return_value=future()
    )

    # act
    result = await create_object_model_from_parsed_offer(
        offer=message
    )

    # assert
    assert get_geo_mock.called
    assert not result
