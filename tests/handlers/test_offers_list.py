import json
from datetime import datetime

import freezegun
import pytest
import pytz
from cian_core.degradation import DegradationResult
from cian_test_utils import future
from freezegun.api import FakeDatetime

from external_offers.entities import Client, Offer
from external_offers.entities.admin import AdminDeleteOfferRequest, AdminUpdateOffersListRequest
from external_offers.entities.teams import Team
from external_offers.enums.teams import TeamType
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
    set_client_to_waiting_status_mock = mocker.patch(
        'external_offers.services.admin.set_client_to_waiting_status_and_return',
        autospec=True
    )
    set_client_to_status_mock = mocker.patch(
        'external_offers.services.admin.set_client_to_status_and_send_kafka_message',
        autospec=True
    )
    client = Client(
        client_id='1',
        avito_user_id='1',
        client_phones=['test'],
        status='inProgress'
    )
    get_client_mock.return_value = future(client)
    offer = Offer(
        id='1',
        parsed_id='parsed',
        client_id='client',
        status='inProgress',
        created_at=datetime.now(pytz.utc),
        parsed_created_at=datetime.now(pytz.utc),
        synced_at=datetime.now(pytz.utc),
    )
    get_offer_mock.return_value = future(offer)
    exist_mock.return_value = future(False)
    set_published_mock.return_value = future()
    save_event_log_mock.return_value = future()
    exist_draft_mock.return_value = future(False)
    set_client_to_waiting_status_mock.return_value = future()
    set_client_to_status_mock.return_value = future()

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
    set_client_to_status_mock.assert_has_calls([
        mocker.call(
            client=client,
            offer=offer,
            set_client_to_status=set_client_to_waiting_status_mock,
        )
    ])
    # set_client_to_waiting_status_mock.assert_has_calls(
    #     [
    #         mocker.call(
    #             client_id='1'
    #         )
    #     ]
    # )


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

    request = AdminUpdateOffersListRequest(is_test=False)

    # act & assert
    with pytest.raises(DegradationException, match=error_message):
        await update_offers_list(request, user_id=realty_user_id)


@pytest.mark.gen_test
async def test_offers_list_page_handler(mocker, http_client, base_url):
    user_id = '1'
    client = Client(
        client_id='1',
        avito_user_id='1',
        client_phones=['7343433'],
        status='inProgress'
    )
    is_calltracking = False
    # client = mocker.MagicMock(value=None)
    offers = mocker.MagicMock(value=[])
    mocker.patch(
        'external_offers.web.handlers.admin.get_team_by_id',
        return_value=future(Team(
            team_id=1,
            team_type=TeamType.attractor,
            team_name='team1',
            lead_id='1',
            settings=json.dumps({
                'enable_only_unhunted_ct': False,
            })
        ))
    )
    mocker.patch(
        'external_offers.web.handlers.admin.get_client_in_progress_by_operator',
        return_value=future(client),
    )
    mocker.patch(
        'external_offers.web.handlers.admin.get_enriched_offers_in_progress_by_operator',
        return_value=future(offers),
    )
    get_offers_list_html_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_offers_list_html',
        return_value='',
    )
    get_operator_roles_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_operator_roles',
        return_value=future([]),
    )
    mocker.patch(
        'external_offers.web.handlers.admin.get_client_is_calltracking_by_client_id',
        return_value=future(is_calltracking),
    )
    current_operator = mocker.MagicMock(is_teamlead=True)
    mocker.patch(
        'external_offers.services.operator_roles.get_enriched_operator_by_id',
        return_value=future(current_operator)
    )
    # act
    with freezegun.freeze_time('2022-01-01'):
        await http_client.fetch(
            base_url+'/admin/offers-list/',
            method='GET',
            headers={
                'X-Real-UserId': user_id,
            },
        )

    # assert
    get_offers_list_html_mock.assert_called_once_with(
        client_is_calltracking=is_calltracking,
        offers=offers,
        client=client,
        client_comment='',
        call_to_phone=client.client_phones[0],
        default_next_call_datetime=FakeDatetime(2022, 1, 2, 10, 0),
        operator_is_tester=False,
        operator_id=int(user_id),
        is_commercial_moderator=False,
        current_operator=current_operator,
        operator_can_call_unhunted_ct=False,
        default_real_phone_hunted_at=mocker.ANY,
        now=mocker.ANY,
    )
    get_operator_roles_mock.assert_called_once_with(
        operator_id=int(user_id),
    )
