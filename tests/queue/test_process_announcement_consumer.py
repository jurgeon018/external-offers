from datetime import datetime

from cian_test_utils import future

from external_offers.services.announcement import process_announcement


async def test_process_announcement_consumer__row_version_is_none__functions_are_not_called(
    mocker
):
    # arrange
    set_offer_publication_status_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.set_offer_publication_status_by_offer_cian_id'
    )
    set_client_unactivated_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.set_client_unactivated_by_offer_cian_id'
    )
    set_client_done_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.set_client_done_by_offer_cian_id'
    )
    set_offer_done_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.set_offer_done_by_offer_cian_id'
    )
    get_offer_row_version_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.get_offer_row_version_by_offer_cian_id'
    )
    object_model = mocker.MagicMock(row_version=None)
    event_date = datetime.now()
    # act
    result = await process_announcement(
        object_model=object_model,
        event_date=event_date,
    )
    # assert
    set_offer_publication_status_by_offer_cian_id_mock.assert_not_called()
    set_client_unactivated_by_offer_cian_id_mock.assert_not_called()
    set_client_done_by_offer_cian_id_mock.assert_not_called()
    set_offer_done_by_offer_cian_id_mock.assert_not_called()
    get_offer_row_version_by_offer_cian_id_mock.assert_not_called()
    assert result is None


async def test_process_announcement_consumer__offer_row_version_is_bigger__functions_are_not_called(
    mocker
):
    # arrange
    offer_row_version = 2
    announcement_row_version = 1
    offer_cian_id = 100
    set_offer_publication_status_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.set_offer_publication_status_by_offer_cian_id'
    )
    set_client_unactivated_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.set_client_unactivated_by_offer_cian_id'
    )
    set_client_done_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.set_client_done_by_offer_cian_id'
    )
    set_offer_done_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.set_offer_done_by_offer_cian_id'
    )
    get_offer_row_version_by_offer_cian_id_mock = mocker.patch(
        'external_offers.services.announcement.get_offer_row_version_by_offer_cian_id',
        return_value=future(offer_row_version)
    )
    object_model = mocker.MagicMock(
        row_version=announcement_row_version,
        cian_id=offer_cian_id,
    )
    event_date = datetime.now()
    # act
    result = await process_announcement(
        object_model=object_model,
        event_date=event_date,
    )
    # assert
    set_offer_publication_status_by_offer_cian_id_mock.assert_not_called()
    set_client_unactivated_by_offer_cian_id_mock.assert_not_called()
    set_client_done_by_offer_cian_id_mock.assert_not_called()
    set_offer_done_by_offer_cian_id_mock.assert_not_called()
    get_offer_row_version_by_offer_cian_id_mock.assert_called_once_with(offer_cian_id)
    assert result is None
