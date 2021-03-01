from external_offers.services.parsed_offers import (
    DEFAULT_ROOMS_COUNT,
    FlatType,
    get_flat_type_from_source_object_model,
    get_rooms_count_from_source_object_model,
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
