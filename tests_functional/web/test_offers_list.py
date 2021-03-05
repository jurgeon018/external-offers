import os
import re
from datetime import datetime, timedelta

import pytest
import pytz


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

    html = resp.body.decode('utf-8')
    html_without_dynamic_datetime = re.sub(
        r'<input id="call-later-datetime" type="datetime-local" value=([\d\:\-T]*)>',
        '',
        html
    )

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_with_client_in_progress_html.write_text(html_without_dynamic_datetime)

    # assert
    assert html_without_dynamic_datetime == (admin_external_offers_operator_with_client_in_progress_html
                                             .read_text('utf-8'))


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

    html = resp.body.decode('utf-8')
    html_without_dynamic_datetime = re.sub(
        r'<input id="call-later-datetime" type="datetime-local" value=([\d\:\-T]*)>',
        '',
        html
    )

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_with_client_cancelled_html.write_text(html_without_dynamic_datetime)

    # assert
    assert html_without_dynamic_datetime == (admin_external_offers_operator_with_client_cancelled_html
                                             .read_text('utf-8'))


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
    html = resp.body.decode('utf-8')
    html_without_dynamic_datetime = re.sub(
        r'<input id="call-later-datetime" type="datetime-local" value=([\d\:\-T]*)>',
        '',
        html
    )

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_without_client_html.write_text(html_without_dynamic_datetime)

    # assert
    assert html_without_dynamic_datetime == (admin_external_offers_operator_without_client_html
                                             .read_text('utf-8'))


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


async def test_update_offers_list__first_operator_without_client__updates_first_by_priority(
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
    assert offers_event_log[0]['offer_id'] == '4'
    assert offers_event_log[0]['status'] == 'inProgress'


async def test_update_offers_list__second_operator_without_client_update__updates_second_by_priority(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    first_operator_without_offers_in_progress = 60024636
    second_operator_without_offers_in_progress = 60024637
    expected_operator_client = '2'
    expected_operator_offer = '3'

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
    assert offers_event_log_first_operator[0]['offer_id'] == '4'
    assert offers_event_log_first_operator[0]['status'] == 'inProgress'

    offers_event_log_second_operator = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [second_operator_without_offers_in_progress]
    )
    assert offers_event_log_second_operator[0]['offer_id'] == '3'
    assert offers_event_log_second_operator[0]['status'] == 'inProgress'


async def test_update_offers_list__exist_suitable_call_later_for_operator_in_queue__set_in_progress(
        pg,
        http,
):
    # arrange
    operator_with_call_later = 60024636
    expected_operator_offer = '1'
    expected_operator_client = '7'
    next_call = datetime.now() - timedelta(hours=1)

    await pg.execute(
        """
        INSERT INTO public.offers_for_call(
            id,
            parsed_id,
            client_id,
            status,
            created_at,
            started_at,
            synced_at,
            last_call_id
        ) VALUES (
            '1',
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            'callLater',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            'ddd86dec-20f5-4a70-bb3a-077b2754df77'
            )
        """
    )
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status,
            next_call

        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', operator_with_call_later,
         'callLater', next_call]
    )

    # act
    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_with_call_later
        },
        expected_status=200)

    # assert
    offer = await pg.fetchrow(
        """SELECT * FROM offers_for_call
           WHERE id=$1 AND status = 'inProgress'""",
        [expected_operator_offer]
    )
    client = await pg.fetchrow(
        """SELECT * FROM clients
           WHERE client_id=$1 AND status = 'inProgress'""",
        [expected_operator_client]
    )
    event_log = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [operator_with_call_later]
    )

    assert offer['id'] == expected_operator_offer
    assert client['operator_user_id'] == operator_with_call_later
    assert event_log[0]['offer_id'] == expected_operator_offer
    assert event_log[0]['status'] == 'inProgress'


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
    assert offers_event_log[0]['offer_id'] == '6'
    assert offers_event_log[0]['status'] == 'declined'
    assert offers_event_log[1]['offer_id'] == '10'
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
    assert offers_event_log[0]['offer_id'] == '6'
    assert offers_event_log[0]['status'] == 'callMissed'
    assert offers_event_log[1]['offer_id'] == '10'
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

    assert offers_event_log[0]['offer_id'] == '8'
    assert offers_event_log[0]['status'] == 'cancelled'
    assert offers_event_log[1]['offer_id'] == '9'
    assert offers_event_log[1]['status'] == 'cancelled'
    assert row_client['operator_user_id'] == 60024649
    assert row_client['status'] == 'waiting'


async def test_delete_offer__exist_offers_in_progress__client_accepted_if_no_offers_in_progress_and_draft(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_user_id = 70024649
    operator_client = '7'
    offer_in_progress = '13'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/delete-offer/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offer_id': offer_in_progress,
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow('SELECT operator_user_id, status FROM clients '
                                   'WHERE client_id=$1',
                                   [operator_client])

    assert row_client['operator_user_id'] is None
    assert row_client['status'] == 'accepted'


async def test_update_offers_list__exist_no_client_waiting__returns_no_success(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute("""UPDATE offers_for_call SET status='inProgress'""")
    await pg.execute("""UPDATE clients SET status='inProgress'""")
    operator = 70024649

    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator
        },
        expected_status=200
    )

    # assert
    assert not resp.data['success']
    assert resp.data['errors']
    assert resp.data['errors'][0]['code'] == 'offersInProgressExist'


async def test_update_offers_list__exist_no_suitable_client__returns_no_success(
        http,
):
    # arrange
    operator = 70024649

    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator
        },
        expected_status=200
    )

    # assert
    assert not resp.data['success']
    assert resp.data['errors']
    assert resp.data['errors'][0]['code'] == 'suitableClientMissing'


async def test_call_later_client__operator_and_in_progress__operator_call_later_priority_set(
        pg,
        http,
        offers_and_clients_fixture,
        runtime_settings
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_client = '1'
    operator = 60024635
    expected_priority = 10
    expected_next_call = datetime.now(pytz.utc)
    await runtime_settings.set({
        'CALL_LATER_PRIORITY': expected_priority
    })

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-later-client/',
        headers={
            'X-Real-UserId': operator
        },
        json={
            'client_id': operator_client,
            'call_later_datetime': expected_next_call.isoformat()
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow('SELECT * FROM clients '
                                   'WHERE client_id=$1',
                                   [operator_client])

    row_offer = await pg.fetchrow('SELECT *, status FROM offers_for_call '
                                  'WHERE client_id=$1',
                                  [operator_client])

    assert row_client['operator_user_id'] == operator
    assert row_client['status'] == 'callLater'
    assert row_client['next_call'] == expected_next_call
    assert row_offer['priority'] == expected_priority


async def test_call_later_client__exist_offers_in_progress_and_cancelled__only_offers_in_progress_set_call_later(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_user_id = 60024636
    operator_client = '4'
    offer_expected_call_later = '6'
    offer_expected_cancelled = '7'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-later-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'client_id': operator_client,
            'call_later_datetime': datetime.now(pytz.utc).isoformat()
        },
        expected_status=200
    )

    # assert
    row_offer_expected_call_later = await pg.fetchrow('SELECT status FROM offers_for_call '
                                                      'WHERE id=$1',
                                                      [offer_expected_call_later])
    row_offer_expected_cancelled = await pg.fetchrow('SELECT status FROM offers_for_call '
                                                     'WHERE id=$1',
                                                     [offer_expected_cancelled])
    offers_event_log = await pg.fetch('SELECT * FROM event_log where operator_user_id=$1', [operator_user_id])

    assert row_offer_expected_call_later['status'] == 'callLater'
    assert row_offer_expected_cancelled['status'] == 'cancelled'
    assert offers_event_log[0]['offer_id'] == '6'
    assert offers_event_log[0]['status'] == 'callLater'
    assert offers_event_log[1]['offer_id'] == '10'
    assert offers_event_log[1]['status'] == 'callLater'


async def test_decline_client__exist_draft__client_accepted(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_user_id = 70024649
    operator_client = '7'
    offer_in_progress = '13'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/decline-client/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offer_id': offer_in_progress,
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow('SELECT operator_user_id, status FROM clients '
                                   'WHERE client_id=$1',
                                   [operator_client])

    assert row_client['operator_user_id'] is None
    assert row_client['status'] == 'accepted'


@pytest.mark.parametrize(
    'method_name',
    [
        'decline-client',
        'call-missed-client',
        'call-later-client',
        'delete-offer',
    ]
)
async def test_call_offer_list_method__missing_client__return_error(
        http,
        method_name,
):
    # arrange
    operator_user_id = 70024649
    operator_client = 'missing'
    offer_in_progress = '13'

    # act
    response = await http.request(
        'POST',
        f'/api/admin/v1/{method_name}/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offer_id': offer_in_progress,
            'client_id': operator_client,
            'call_later_datetime': datetime.now(pytz.utc).isoformat()
        },
        expected_status=200
    )

    # assert
    assert response.data['errors'] == [
        {
            'message': 'Пользователь с переданным идентификатором не найден',
            'code': 'missingUser'
        }
    ]


async def test_call_delete_offer_method__missing_offer__return_error(
        http,
        offers_and_clients_fixture,
        pg
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_user_id = 70024649
    operator_client = '7'
    offer_in_progress = 'missing'

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/delete-offer/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offer_id': offer_in_progress,
            'client_id': operator_client
        },
        expected_status=200
    )

    # assert
    assert response.data['errors'] == [
        {
            'message': 'Объявление с переданным идентификатором не найдено',
            'code': 'missingOffer'
        }
    ]
