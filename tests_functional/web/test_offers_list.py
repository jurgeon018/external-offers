import os

import pytest
from cian_json import json


async def test_get_offers_list__without_x_real_userid__returns_400(http):
    # act && assert
    await http.request('GET', '/admin/offers-list/', expected_status=400)


@pytest.mark.html
async def test_get_offers_list__operator_with_client_in_progress__returns_offers_in_progress_page(
        http,
        pg,
        admin_external_offers_operator_with_client_in_progress_html,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_client = 60024635

    # act
    resp = await http.request(
        'GET',
        '/admin/offers-list/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200)

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_with_client_in_progress_html.write_text(resp.body.decode('utf-8'))

    # assert
    assert resp.body.decode('utf-8') == admin_external_offers_operator_with_client_in_progress_html.read_text('utf-8')


@pytest.mark.html
async def test_get_offers_list__operator_with_client_cancelled__returns_no_offers_page(
        http,
        pg,
        offers_and_clients_fixture,
        admin_external_offers_operator_with_client_cancelled_html,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_client = 60024636

    # act
    resp = await http.request(
        'GET',
        '/admin/offers-list/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200)

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_with_client_cancelled_html.write_text(resp.body.decode('utf-8'))

    # assert
    assert resp.body.decode('utf-8') == admin_external_offers_operator_with_client_cancelled_html.read_text('utf-8')


@pytest.mark.html
async def test_get_offers__operator_without_client__returns_no_offers_page(
        pg,
        http,
        admin_external_offers_operator_without_client_html,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_without_clients = 1

    # act
    resp = await http.request(
        'GET',
        '/admin/offers-list/',
        headers={
            'X-Real-UserId': operator_without_clients
        },
        expected_status=200)

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_without_client_html.write_text(resp.body.decode('utf-8'))

    # assert
    assert resp.body.decode('utf-8') == admin_external_offers_operator_without_client_html.read_text('utf-8')


async def test_update_offers_list__operator_with_client_in_progress__returns_not_success(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_offers_in_progress = 60024635

    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_with_offers_in_progress
        },
        expected_status=200)

    # assert
    assert not resp.data['success']
    assert resp.data['errors']


async def test_update_offers_list__operator_without_client__returns_success(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_without_offers_in_progress = 60024636

    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_without_offers_in_progress
        },
        expected_status=200)

    # assert
    assert resp.data['success']
    assert not resp.data['errors']


async def test_update_offers_list__first_operator_without_client__updates_first_created(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_without_offers_in_progress = 60024636
    expected_operator_client = '3'
    expected_operator_offer = '4'
    # act
    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_without_offers_in_progress
        },
        expected_status=200)

    # assert
    assert operator_without_offers_in_progress == await pg.fetchval("""SELECT operator_user_id FROM clients
                                                                       WHERE client_id=$1
                                                                       AND status='inProgress'""",
                                                                    [expected_operator_client])

    assert expected_operator_offer == await pg.fetchval("""SELECT id FROM offers_for_call
                                                           WHERE client_id=$1 AND status = 'inProgress'""",
                                                        [expected_operator_client])
    offers_event_log = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [operator_without_offers_in_progress]
    )
    assert offers_event_log[0]['offer_id'] == '9999d421-b7ba-4ee0-b29f-bc8add87c933'
    assert offers_event_log[0]['status'] == 'inProgress'


async def test_update_offers_list__second_operator_without_client_update__updates_second_created(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    first_operator_without_offers_in_progress = 60024636
    second_operator_without_offers_in_progress = 60024637
    expected_operator_client = '2'
    expected_operator_offer = '5'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': first_operator_without_offers_in_progress
        },
        expected_status=200)

    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': second_operator_without_offers_in_progress
        },
        expected_status=200)

    # assert
    assert second_operator_without_offers_in_progress == await pg.fetchval('SELECT operator_user_id FROM clients '
                                                                           'WHERE client_id=$1',
                                                                           [expected_operator_client])

    assert expected_operator_offer == await pg.fetchval("SELECT id FROM offers_for_call "
                                                        "WHERE client_id=$1 AND status = 'inProgress'",
                                                        [expected_operator_client])

    offers_event_log_first_operator = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [first_operator_without_offers_in_progress]
    )
    assert offers_event_log_first_operator[0]['offer_id'] == '9999d421-b7ba-4ee0-b29f-bc8add87c933'
    assert offers_event_log_first_operator[0]['status'] == 'inProgress'

    offers_event_log_second_operator = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [second_operator_without_offers_in_progress]
    )
    assert offers_event_log_second_operator[0]['offer_id'] == '33e4d51e-e8d3-499d-9497-4229d6c539ee'
    assert offers_event_log_second_operator[0]['status'] == 'inProgress'


async def test_decline_client__no_operator_and_in_progress__still_no_operator_and_declined(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator = 60024636
    client_id = '2'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/decline-client/',
        headers={
            'X-Real-UserId': operator
        },
        json={
            'client_id': client_id
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow('SELECT operator_user_id, status FROM clients '
                                   'WHERE client_id=$1',
                                   [client_id])

    assert row_client['operator_user_id'] is None
    assert row_client['status'] == 'declined'


async def test_decline_client__client_with_cancelled_and_in_progress__only_in_progress_set_declined(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_user_id = 60024636
    operator_client = '4'
    offer_expected_declined = '6'
    offer_expected_cancelled = '7'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/decline-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    row_offer_expected_declined = await pg.fetchrow('SELECT status FROM offers_for_call '
                                                    'WHERE id=$1',
                                                    [offer_expected_declined])
    row_offer_expected_cancelled = await pg.fetchrow('SELECT status FROM offers_for_call '
                                                     'WHERE id=$1',
                                                     [offer_expected_cancelled])
    offers_event_log = await pg.fetch('SELECT * FROM event_log where operator_user_id=$1', [operator_user_id])

    assert row_offer_expected_declined['status'] == 'declined'
    assert row_offer_expected_cancelled['status'] == 'cancelled'
    assert offers_event_log[0]['offer_id'] == 'wrong-parsed-id'
    assert offers_event_log[0]['status'] == 'declined'
    assert offers_event_log[1]['offer_id'] == 'wrong-parsed-id-2'
    assert offers_event_log[1]['status'] == 'declined'


async def test_call_missed_client__no_operator_and_in_progress__still_no_operator_and_call_missed(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator = 60024636
    operator_client = '2'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-missed-client/',
        headers={
            'X-Real-UserId': operator
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow('SELECT operator_user_id, status FROM clients '
                                   'WHERE client_id=$1',
                                   [operator_client])

    assert row_client['operator_user_id'] is None
    assert row_client['status'] == 'callMissed'


async def test_call_missed_client__exist_offers_in_progress_and_cancelled__only_offers_in_progress_set_call_missed(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_user_id = 60024636
    operator_client = '4'
    offer_expected_call_missed = '6'
    offer_expected_cancelled = '7'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-missed-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    row_offer_expected_call_missed = await pg.fetchrow('SELECT status FROM offers_for_call '
                                                       'WHERE id=$1',
                                                       [offer_expected_call_missed])
    row_offer_expected_cancelled = await pg.fetchrow('SELECT status FROM offers_for_call '
                                                     'WHERE id=$1',
                                                     [offer_expected_cancelled])
    offers_event_log = await pg.fetch('SELECT * FROM event_log where operator_user_id=$1', [operator_user_id])

    assert row_offer_expected_call_missed['status'] == 'callMissed'
    assert row_offer_expected_cancelled['status'] == 'cancelled'
    assert offers_event_log[0]['offer_id'] == 'wrong-parsed-id'
    assert offers_event_log[0]['status'] == 'callMissed'
    assert offers_event_log[1]['offer_id'] == 'wrong-parsed-id-2'
    assert offers_event_log[1]['status'] == 'callMissed'


async def test_delete_offer__exist_offers_in_progress__only_one_offer_cancelled(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator = 60024649
    operator_client = '5'
    offer_id = '8'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/delete-offer/',
        headers={
            'X-Real-UserId': operator
        },
        json={
            'offer_id': offer_id,
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow('SELECT operator_user_id, status FROM clients '
                                   'WHERE client_id=$1',
                                   [operator_client])
    row_offer = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE id=$1
        """,
        [offer_id]
    )

    assert row_client['status'] == 'inProgress'
    assert row_offer['status'] == 'cancelled'


async def test_delete_offer__exist_offers_in_progress__client_waiting_if_no_offers_in_progress(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_user_id = 60024649
    operator_client = '5'
    first_offer_id = '8'
    second_offer_id = '9'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/delete-offer/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offer_id': first_offer_id,
            'client_id': operator_client
        },
        expected_status=200
    )

    await http.request(
        'POST',
        '/api/admin/v1/delete-offer/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offer_id': second_offer_id,
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow('SELECT operator_user_id, status FROM clients '
                                   'WHERE client_id=$1',
                                   [operator_client])
    offers_event_log = await pg.fetch('SELECT * FROM event_log where operator_user_id=$1', [operator_user_id])

    assert row_client['status'] == 'waiting'
    assert offers_event_log[0]['offer_id'] == '8'
    assert offers_event_log[0]['status'] == 'cancelled'
    assert offers_event_log[1]['offer_id'] == '9'
    assert offers_event_log[1]['status'] == 'cancelled'
