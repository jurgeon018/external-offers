from datetime import datetime

import pytest
import pytz
from cian_core.degradation import DegradationResult
from cian_test_utils import future

from external_offers.entities import Client, Offer
from external_offers.entities.admin import AdminDeleteOfferRequest
from external_offers.helpers.errors import USER_ROLES_REQUEST_MAX_TRIES_ERROR, DegradationException
from external_offers.services.admin import already_published_offer, update_offers_list
from external_offers.settings.base import EXTERNAL_OFFERS_GET_USER_ROLES_TRIES_COUNT


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
            parsed_created_at=datetime.now(pytz.utc),
            synced_at=datetime.now(pytz.utc),
        )
    )
    exist_mock.return_value = future(False)
    set_published_mock.return_value = future()
    save_event_log_mock.return_value = future()
    exist_draft_mock.return_value = future(False)
    set_client_status_mock.return_value = future()

    operator_user_id = 1
    request = AdminDeleteOfferRequest(
        client_id='1',
        offer_id='2'
    )

    # act
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


async def test_update_offers_list__operator_roles_request_degraded(mocker):
    # arrange
    realty_user_id = 123

    mocker.patch(
        'external_offers.services.admin.exists_offers_in_progress_by_operator',
        return_value=future(False),
    )

    mocker.patch(
        'external_offers.services.operator_roles.v1_get_user_roles_with_degradation',
        return_value=future(DegradationResult(degraded=True, value={'roles': []}))
    )

    error_message = USER_ROLES_REQUEST_MAX_TRIES_ERROR % {
        'user_id': realty_user_id,
        'tries': EXTERNAL_OFFERS_GET_USER_ROLES_TRIES_COUNT
    }

    # act & assert
    with pytest.raises(DegradationException, match=error_message):
        await update_offers_list(user_id=realty_user_id)
