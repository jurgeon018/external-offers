from datetime import datetime

import pytest
import pytz
from cian_core.runtime_settings import runtime_settings
from cian_test_utils import future
from simple_settings.utils import settings_stub

from external_offers.entities.offers import Offer
from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import Status as PublicationStatus


@pytest.mark.gen_test
async def test_get_admin_offer_card__exist_drafts__called_correct_get_offer_card_html(
        http_client,
        base_url,
        mocker,
):
    # arrange
    current_operator = mocker.MagicMock(is_teamlead=True)
    mocker.patch(
        'external_offers.services.operator_roles.get_enriched_operator_by_id',
        return_value=future(current_operator)
    )
    mocker.patch(
        'external_offers.web.handlers.admin.runtime_settings',
        new={
            'EXTERNAL_OFFERS_READY_BUSINESS_ENABLED': False,
            'DEBUG': False,
        }
    )
    comment = 'comment'
    is_ready_business_enabled = runtime_settings.get('EXTERNAL_OFFERS_READY_BUSINESS_ENABLED', False)
    save_offer_msg = 'test'
    offer_id = '1'
    exists_offers_mock = mocker.patch('external_offers.web.handlers.admin.exists_offer'
                                      's_in_progress_by_operator_and_offer_id')
    exists_offers_mock.return_value = future(True)

    get_parsed_offer_mock = mocker.patch('external_offers.web.handlers.admin.get_parsed_'
                                         'offer_object_model_by_offer_id')
    get_parsed_offer_mock.return_value = future(mocker.sentinel.parsed_offer)
    get_offer_comment_by_offer_id_mock = mocker.patch(
        'external_offers.web.handlers.admin.get_offer_comment_by_offer_id'
    )
    get_offer_comment_by_offer_id_mock.return_value = future(comment)
    get_client_mock = mocker.patch('external_offers.web.handlers.admin.get_client_in_progress_by_operator')
    client_mock = mocker.MagicMock()
    get_client_mock.return_value = future(client_mock)

    client_accounts_mock = mocker.patch('external_offers.web.handlers.admin.get_client_ac'
                                        'counts_by_phone_number_degradation_handler')
    client_account = mocker.MagicMock(value=[])
    client_accounts_mock.return_value = future(client_account)

    get_possible_appointments_mock = mocker.patch(
        'external_offers.services.possible_appointments.get_possible_appointments_with_degradation'
    )
    appointments = mocker.MagicMock(value=[])
    get_possible_appointments_mock.return_value = future(appointments)

    exist_drafts_mock = mocker.patch('external_offers.web.handlers.admin.exists_offers_draft_by_client')
    exist_drafts_mock.return_value = future(False)

    get_offer_card_html_mock = mocker.patch('external_offers.web.handlers.admin.get_offer_card_html')
    get_offer_card_html_mock.return_value = ''

    offer = Offer(
        id='1',
        parsed_id='parsed',
        client_id='client',
        status='inProgress',
        created_at=datetime.now(pytz.utc),
        parsed_created_at=datetime.now(pytz.utc),
        synced_at=datetime.now(pytz.utc),
        publication_status=PublicationStatus.draft,
    )
    get_offer_by_offer_id_mock = mocker.patch('external_offers.web.handlers.admin.get_offer_by_offer_id')
    get_offer_by_offer_id_mock.return_value = future(offer)

    # act
    with settings_stub(SAVE_OFFER_MSG=save_offer_msg):
        await http_client.fetch(
            base_url+f'/admin/offer-card/{offer_id}/',
            method='GET',
            headers={
                'X-Real-UserId': '1',
            },
        )

    # assert
    get_offer_card_html_mock.assert_has_calls(
        [
            mocker.call(
                parsed_object_model=mocker.sentinel.parsed_offer,
                info_message=save_offer_msg,
                offer_id=offer_id,
                client=client_mock,
                appointments=[],
                client_accounts=[],
                exist_drafts=False,
                offer_is_draft=True,
                is_ready_business_enabled=1 if is_ready_business_enabled is True else 0,
                offer_comment=comment,
                current_operator=current_operator,
            )
        ]
    )
