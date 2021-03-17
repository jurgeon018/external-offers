from datetime import datetime

import pytz
from cian_test_utils import future
from simple_settings.utils import settings_stub

from external_offers.entities import Client, Offer
from external_offers.entities.admin import AdminCallInterruptedClientRequest, AdminDeleteOfferRequest
from external_offers.services.admin import already_published_offer, set_call_interrupted_status_for_client


async def test_already_published_offer__missing_parsed_offer__warning_expected(
    mocker
):
    # arrange
    get_client_mock = mocker.patch(
        'external_offers.services.admin.get_client_by_client_id',
        autospec=True
    )
    get_offer_mock = mocker.patch(
        'external_offers.services.admin.get_offer_by_offer_id',
        autospec=True
    )
    get_parsed_mock = mocker.patch(
        'external_offers.services.admin.get_parsed_offer_by_offer_id',
        autospec=True
    )
    set_published_mock = mocker.patch(
        'external_offers.services.admin.set_offer_already_published_by_offer_id',
        autospec=True
    )
    save_event_log_mock = mocker.patch(
        'external_offers.services.admin.save_event_log_for_offers',
        autospec=True
    )
    exist_mock = mocker.patch(
        'external_offers.services.admin.exists_offers_in_progress_by_client',
        autospec=True
    )
    warning_mock = mocker.patch(
        'external_offers.services.admin.logger.warning',
        autospec=True
    )

    get_client_mock.return_value = future(
        Client(
            client_id='1',
            avito_user_id='1',
            client_phones=['test'],
            status='inProgress'
        )
    )
    get_offer_mock.return_value = future(
        Offer(
            id='1',
            parsed_id='parsed',
            client_id='client',
            status='inProgress',
            created_at=datetime.now(pytz.utc),
            synced_at=datetime.now(pytz.utc)
        )
    )
    exist_mock.return_value = future(True)
    set_published_mock.return_value = future()
    save_event_log_mock.return_value = future()
    get_parsed_mock.return_value = future()

    operator_user_id = 1
    request = AdminDeleteOfferRequest(
        client_id='1',
        offer_id='2'
    )

    # act
    with settings_stub(
        ENABLE_SEND_KAFKA_MESSAGE_FOR_ALREADY_PUBLISHED=True
    ):
        await already_published_offer(
            request=request,
            user_id=operator_user_id
        )

    # assert
    warning_mock.assert_has_calls(
        [
            mocker.call(
                'При отметке уже опубликованного объявления не нашли спаршенное для задания %s',
                '2'
            )
        ]
    )


async def test_already_published_offer__no_in_progress_and_no_draft__set_waiting_call_expected(
    mocker
):
    # arrange
    get_client_mock = mocker.patch(
        'external_offers.services.admin.get_client_by_client_id',
        autospec=True
    )
    get_offer_mock = mocker.patch(
        'external_offers.services.admin.get_offer_by_offer_id',
        autospec=True
    )
    get_parsed_mock = mocker.patch(
        'external_offers.services.admin.get_parsed_offer_by_offer_id',
        autospec=True
    )
    set_published_mock = mocker.patch(
        'external_offers.services.admin.set_offer_already_published_by_offer_id',
        autospec=True
    )
    save_event_log_mock = mocker.patch(
        'external_offers.services.admin.save_event_log_for_offers',
        autospec=True
    )
    exist_mock = mocker.patch(
        'external_offers.services.admin.exists_offers_in_progress_by_client',
        autospec=True
    )
    exist_draft_mock = mocker.patch(
        'external_offers.services.admin.exists_offers_draft_by_client',
        autospec=True
    )
    set_client_status_mock = mocker.patch(
        'external_offers.services.admin.set_client_to_waiting_status_and_return',
        autospec=True
    )

    get_client_mock.return_value = future(
        Client(
            client_id='1',
            avito_user_id='1',
            client_phones=['test'],
            status='inProgress'
        )
    )
    get_offer_mock.return_value = future(
        Offer(
            id='1',
            parsed_id='parsed',
            client_id='client',
            status='inProgress',
            created_at=datetime.now(pytz.utc),
            synced_at=datetime.now(pytz.utc)
        )
    )
    exist_mock.return_value = future(False)
    set_published_mock.return_value = future()
    save_event_log_mock.return_value = future()
    get_parsed_mock.return_value = future()
    exist_draft_mock.return_value = future(False)
    set_client_status_mock.return_value = future()

    operator_user_id = 1
    request = AdminDeleteOfferRequest(
        client_id='1',
        offer_id='2'
    )

    # act
    with settings_stub(
        ENABLE_SEND_KAFKA_MESSAGE_FOR_ALREADY_PUBLISHED=True
    ):
        await already_published_offer(
            request=request,
            user_id=operator_user_id
        )

    # assert
    set_client_status_mock.assert_has_calls(
        [
            mocker.call(
                client_id='1'
            )
        ]
    )
