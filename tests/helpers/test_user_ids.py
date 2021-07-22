from external_offers.helpers.user_id import (
    CIAN_ID_THRESHOLD,
    CIAN_ID_TO_REALTY_ID_FILE,
    get_realty_id_by_cian_id,
    get_user_cian_id_by_realty_id,
)


def test_get_user_cian_id_by_realty_id__id_exists__return_expected():
    assert get_user_cian_id_by_realty_id(6676795) == 500271


def test_get_user_cian_id_by_realty_id__id_less_1__return_expected():
    assert get_user_cian_id_by_realty_id(-1) is None


def test_get_user_cian_id_by_realty_id__id_doesnt_exist__return_none():
    assert get_user_cian_id_by_realty_id(1) == 1


def test_get_user_cian_id_by_realty_id__over_threshold__return_0():
    assert get_user_cian_id_by_realty_id(999999999) == 999999999


def test_get_user_cian_id_by_realty_id(mocker):
    # arrange
    _get_user_id_mock = mocker.patch('external_offers.helpers.user_id._get_user_id', return_value=222,)

    # act
    result = get_realty_id_by_cian_id(111)

    # assert
    assert result == 222
    _get_user_id_mock.assert_called_once_with(
        user_id=111,
        file=CIAN_ID_TO_REALTY_ID_FILE,
        threshold=CIAN_ID_THRESHOLD,
    )
