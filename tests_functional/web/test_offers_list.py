import json
from datetime import datetime, timedelta

import pytest
import pytz
from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_get_offers_list__without_x_real_userid__returns_400(http):
    # act && assert
    await http.request('GET', '/admin/offers-list/', expected_status=400)


@pytest.mark.parametrize('USE_PARSED_OFFERS_FOR_CALLTRACKING_FILTRATION', [
    True,
    False,
])
async def test_update_offers_list_with_unactivated_clients__operator_without_client__return_success(
        pg,
        http,
        offers_and_clients_fixture,
        parsed_offers_for_offers_and_clients_fixture,
        users_mock,
        runtime_settings,
        USE_PARSED_OFFERS_FOR_CALLTRACKING_FILTRATION,
):
    # arrange
    await runtime_settings.set({
        'USE_PARSED_OFFERS_FOR_CALLTRACKING_FILTRATION': USE_PARSED_OFFERS_FOR_CALLTRACKING_FILTRATION,
    })
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_for_offers_and_clients_fixture)

    expected_client = '224'
    expected_offer = '226'
    operator_id = 60024636
    next_call = (datetime.now(pytz.utc) - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S')
    await pg.execute(f"""
        INSERT INTO clients (
            segment, unactivated, client_id, avito_user_id, client_phones, status, next_call, operator_user_id
        ) VALUES
        (NULL,'t',221, 221,'{{+7232121}}','accepted', NULL, NULL),
        ('c', 't',222, 222,'{{+7232122}}','accepted', NULL, NULL),
        ('d', 't',223, 223,'{{+7232123}}','accepted', NULL, NULL),
        ('d', 't',{expected_client},{expected_client},'{{+7232123}}','accepted','{next_call}',{operator_id});
    """)
    await pg.execute(f"""
        INSERT INTO offers_for_call (
            id, parsed_id, client_id, priority, publication_status,status,category,created_at,synced_at,is_calltracking
        ) VALUES
        (221, 221, 221, 1, 'Draft', 'draft', 'flatRent', 'now()', 'now()', 'f'),
        (222, 222, 222, 1, 'Draft', 'draft', 'flatRent', 'now()', 'now()', 'f'),
        (223, 223, 222, 1, 'Draft', 'draft', 'flatRent', 'now()', 'now()', 'f'),
        (224, 224, 223, 1, 'Draft', 'draft', 'flatRent', 'now()', 'now()', 'f'),
        (225, 225, 223, 1, 'Draft', 'draft', 'flatRent', 'now()', 'now()', 'f'),
        ({expected_offer},{expected_offer},{expected_client},1,'Draft','draft','flatRent','now()','now()','f');
    """)
    await pg.execute("""
        INSERT INTO parsed_offers (
            id, source_object_id, source_user_id,source_object_model,is_calltracking,timestamp,created_at,updated_at
        ) VALUES
        (221, 221, 221, '{\"region\": \"4568\"}',     'f', 'now()', 'now()', 'now()'),
        (222, 222, 222, '{\"region\": \"4636\"}',     'f', 'now()', 'now()', 'now()'),
        (223, 223, 222, '{\"region\": \"4624\"}',     'f', 'now()', 'now()', 'now()'),
        (224, 224, 223, '{\"region\": \"4568\"}',     'f', 'now()', 'now()', 'now()'),
        (225, 225, 223, '{\"region\": \"4636\"}',     'f', 'now()', 'now()', 'now()'),
        (226, 226, 224, '{}',                         'f', 'now()', 'now()', 'now()');
    """)
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={
                'roles': [
                    # {'id': 1, 'name': 'CommercialPrepublicationModerator'}
                ],
            }
        ),
    )

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_id
        },
        json={},
        expected_status=200
    )
    body = json.loads(response.body)
    offers_event_log = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [
            operator_id
        ]
    )
    # assert
    assert offers_event_log[0]['offer_id'] == expected_offer
    assert offers_event_log[0]['status'] == 'inProgress'
    assert body['success'] is True
    assert operator_id == await pg.fetchval(
        'SELECT operator_user_id FROM clients WHERE client_id=$1 AND status=$2',
        [
            expected_client,
            'inProgress'
        ]
    )

    assert expected_offer == await pg.fetchval(
        'SELECT id FROM offers_for_call WHERE client_id=$1 AND status = $2',
        [
            expected_client,
            'inProgress'
        ]
    )


async def test_update_offers_list__with_is_test_true__assigns_test_object_to_operator(
    pg,
    http,
    offers_and_clients_fixture,
    parsed_offers_fixture,
    test_objects_fixture,
    users_mock,
):
    # arrange
    operator_user_id = '11111111'
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    await pg.execute_scripts(test_objects_fixture)

    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )

    # act
    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        json={
            'isTest': True,
        },
        headers={
            'X-Real-UserId': operator_user_id
        },
        expected_status=200
    )

    # assert
    clients = await pg.fetch(f"""
        SELECT * FROM clients WHERE operator_user_id='{operator_user_id}'
    """)
    assert len(clients) == 1
    assert clients[0]['is_test'] is True


async def test_update_offers_list__operator_with_client_in_progress__returns_not_success(
        pg,
        http,
        offers_and_clients_fixture,
        parsed_offers_fixture,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    operator_with_offers_in_progress = 60024635

    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_with_offers_in_progress
        },
        json={},
        expected_status=200
    )

    # assert
    assert not resp.data['success']
    assert resp.data['errors']


async def test_update_offers_list__operator_without_client__returns_success(
        pg,
        http,
        offers_and_clients_fixture,
        parsed_offers_for_offers_and_clients_fixture,
        users_mock,
):
    # arrange
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )

    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_for_offers_and_clients_fixture)
    operator_without_offers_in_progress = 60024636

    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_without_offers_in_progress
        },
        json={},
        expected_status=200
    )

    # assert
    assert resp.data['success']
    assert not resp.data['errors']


async def test_update_offers_list__first_operator_without_client__updates_first_by_priority(
        pg,
        http,
        offers_and_clients_fixture,
        parsed_offers_for_offers_and_clients_fixture,
        users_mock,
):
    # arrange
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )

    await pg.execute_scripts(parsed_offers_for_offers_and_clients_fixture)
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
        json={},
        expected_status=200
    )

    # assert
    offers_event_log = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [
            operator_without_offers_in_progress
        ]
    )

    assert operator_without_offers_in_progress == await pg.fetchval(
        'SELECT operator_user_id FROM clients WHERE client_id=$1 AND status=$2',
        [
            expected_operator_client,
            'inProgress'
        ]
    )

    assert expected_operator_offer == await pg.fetchval(
        'SELECT id FROM offers_for_call WHERE client_id=$1 AND status = $2',
        [
            expected_operator_client,
            'inProgress'
        ]
    )
    assert offers_event_log[0]['offer_id'] == '4'
    assert offers_event_log[0]['status'] == 'inProgress'


async def test_update_offers_list__second_operator_without_client_update__updates_second_by_priority(
        pg,
        http,
        offers_and_clients_fixture,
        parsed_offers_for_offers_and_clients_fixture,
        users_mock,
):
    # arrange
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )

    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_for_offers_and_clients_fixture)
    first_operator_without_offers_in_progress = 60024636
    second_operator_without_offers_in_progress = 60024637
    expected_operator_client = '2'
    # expected_operator_offer = '3'
    expected_operator_offer = '5'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': first_operator_without_offers_in_progress
        },
        json={},
        expected_status=200
    )

    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': second_operator_without_offers_in_progress
        },
        json={},
        expected_status=200)

    # assert
    offers_event_log_first_operator = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [
            first_operator_without_offers_in_progress
        ]
    )

    offers_event_log_second_operator = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [
            second_operator_without_offers_in_progress
        ]
    )

    assert second_operator_without_offers_in_progress == await pg.fetchval(
        'SELECT operator_user_id FROM clients WHERE client_id=$1',
        [
            expected_operator_client
        ]
    )

    assert expected_operator_offer == await pg.fetchval(
        'SELECT id FROM offers_for_call WHERE client_id=$1 AND status = $2',
        [
            expected_operator_client,
            'inProgress'
        ]
    )

    assert offers_event_log_first_operator[0]['offer_id'] == '4'
    assert offers_event_log_first_operator[0]['status'] == 'inProgress'

    assert offers_event_log_second_operator[0]['offer_id'] == expected_operator_offer
    assert offers_event_log_second_operator[0]['status'] == 'inProgress'


@pytest.mark.parametrize('status', ('callLater', 'callMissed'))
async def test_update_offers_list__exist_suitable_next_call_for_operator_in_queue__set_in_progress(
        pg,
        http,
        status,
        users_mock,
):
    # arrange
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )

    operator_with_call_later = 60024636
    expected_operator_offer = '1'
    expected_operator_client = '7'
    now = datetime.now(pytz.utc)
    next_call = datetime.now() - timedelta(hours=1)

    await pg.execute(
        """
        INSERT INTO public.offers_for_call(
            id,
            priority,
            parsed_id,
            client_id,
            status,
            created_at,
            started_at,
            synced_at,
            last_call_id
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        [
            '1',
            231120211,
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            status,
            now,
            now,
            now,
            'ddd86dec-20f5-4a70-bb3a-077b2754df77'
        ]
    )
    await pg.execute(
        """
        INSERT INTO public.parsed_offers(
        id,
        user_segment,
        source_object_id,
        source_user_id,
        source_object_model,
        is_calltracking,
        "timestamp",
        created_at,
        updated_at
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        """,
        [
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            'NOT_IMPORTANT',
            '1_1',
            '1',
            '{}',
            False,
            now,
            now,
            now
        ]
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
        [
            '7',
            '555bb598767308327e1dffbe7241486c',
            '???????? ????????????',
            ['+79812333292'],
            'nemoy@gmail.com',
            operator_with_call_later,
            status,
            next_call
        ]
    )

    # act
    await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_with_call_later
        },
        json={},
        expected_status=200
    )

    # assert
    offer = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE id=$1 AND status = $2',
        [
            expected_operator_offer,
            'inProgress'
        ]
    )
    client = await pg.fetchrow(
        'SELECT * FROM clients WHERE client_id=$1 AND status = $2',
        [
            expected_operator_client,
            'inProgress'
        ]
    )
    event_log = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [
            operator_with_call_later
        ]
    )

    assert offer['id'] == expected_operator_offer
    assert client['operator_user_id'] == operator_with_call_later
    assert event_log[0]['offer_id'] == expected_operator_offer
    assert event_log[0]['status'] == 'inProgress'


@pytest.mark.parametrize(
    ['method_name', 'expected_status_for_in_progress'],
    [
        ['decline-client', 'declined'],
        ['call-interrupted-client', 'callInterrupted'],
        ['phone-unavailable-client', 'phoneUnavailable'],
        ['promo-given-client', 'promoGiven']
    ]
)
async def test_client_status_change__client_with_cancelled_and_in_progress__only_in_progress_set_new_status(
        pg,
        method_name,
        expected_status_for_in_progress,
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
        f'/api/admin/v1/{method_name}/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    row_offer_expected_declined = await pg.fetchrow(
        'SELECT status FROM offers_for_call WHERE id=$1',
        [
            offer_expected_declined
        ]
    )
    row_offer_expected_cancelled = await pg.fetchrow(
        'SELECT status FROM offers_for_call WHERE id=$1',
        [
            offer_expected_cancelled
        ]
    )
    offers_event_log = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [
            operator_user_id
        ]
    )

    assert row_offer_expected_declined['status'] == expected_status_for_in_progress
    assert row_offer_expected_cancelled['status'] == 'cancelled'
    assert offers_event_log[0]['offer_id'] == '10'
    assert offers_event_log[0]['status'] == expected_status_for_in_progress
    assert offers_event_log[1]['offer_id'] == '6'
    assert offers_event_log[1]['status'] == expected_status_for_in_progress


async def test_call_missed_client__operator_and_in_progress__next_call_and_call_missed_priority_set(
        pg,
        http,
        runtime_settings,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator = 60024635
    operator_client = '1'
    expected_priority = 200000

    expected_next_call = datetime.now(pytz.utc) + timedelta(days=1)
    expected_next_call_left_border = expected_next_call - timedelta(minutes=1)
    expected_next_call_right_border = expected_next_call + timedelta(minutes=1)

    await runtime_settings.set({
        'CALL_MISSED_PRIORITY': 2
    })

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-missed-client/',
        headers={
            'X-Real-UserId': operator
        },
        json={
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow(
        'SELECT * FROM clients WHERE client_id=$1',
        [
            operator_client
        ]
    )

    row_offer = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE client_id=$1',
        [
            operator_client
        ]
    )

    assert row_client['operator_user_id'] == operator
    assert row_client['status'] == 'callMissed'
    assert row_offer['status'] == 'callMissed'
    assert row_offer['priority'] == expected_priority
    assert expected_next_call_left_border <= row_client['next_call'] < expected_next_call_right_border


async def test_call_missed_client__operator_and_in_progress__next_call_and_call_missed_team_priority_set(
        pg,
        http,
        runtime_settings,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator = 60024635
    operator_client = '1'
    expected_priority = 200000

    expected_next_call = datetime.now(pytz.utc) + timedelta(days=1)
    expected_next_call_left_border = expected_next_call - timedelta(minutes=1)
    expected_next_call_right_border = expected_next_call + timedelta(minutes=1)

    await runtime_settings.set({
        'CALL_MISSED_PRIORITY': 2
    })

    # act
    await pg.execute("""
    INSERT INTO operators (
        operator_id, full_name, team_id, is_teamlead, created_at, updated_at
    ) VALUES (
        $1, $2, $3, 't', 'now()', 'now()'
    )
    """, [str(operator), '???????????????? ???1', 1])

    await http.request(
        'POST',
        '/api/admin/v1/create-team-public/',
        json={
            'teamName': '?????????????? ???1',
            'leadId': str(operator),
            'teamType': 'attractor',
        },
        headers={
            'X-Real-UserId': operator
        },
        expected_status=200
    )
    await http.request(
        'POST',
        '/api/admin/v1/call-missed-client/',
        headers={
            'X-Real-UserId': operator
        },
        json={
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow(
        'SELECT * FROM clients WHERE client_id=$1',
        [
            operator_client
        ]
    )

    row_offer = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE client_id=$1',
        [
            operator_client
        ]
    )

    assert row_client['operator_user_id'] == operator
    assert row_client['status'] == 'callMissed'
    assert row_offer['status'] == 'callMissed'
    assert json.loads(row_offer['team_priorities'])['1'] == expected_priority
    assert expected_next_call_left_border <= row_client['next_call'] < expected_next_call_right_border


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
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    row_offer_expected_call_missed = await pg.fetchrow(
        'SELECT status FROM offers_for_call WHERE id=$1',
        [
            offer_expected_call_missed
        ]
    )
    row_offer_expected_cancelled = await pg.fetchrow(
        'SELECT status FROM offers_for_call WHERE id=$1',
        [
            offer_expected_cancelled
        ]
    )
    offers_event_log = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [
            operator_user_id
        ]
    )

    assert row_offer_expected_call_missed['status'] == 'callMissed'
    assert row_offer_expected_cancelled['status'] == 'cancelled'
    assert offers_event_log[0]['offer_id'] == '10'
    assert offers_event_log[0]['status'] == 'callMissed'
    assert offers_event_log[1]['offer_id'] == '6'
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
    offerId = '8'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/delete-offer/',
        headers={
            'X-Real-UserId': operator
        },
        json={
            'offerId': offerId,
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow(
        'SELECT operator_user_id, status FROM clients WHERE client_id=$1',
        [
            operator_client
        ]
    )
    row_offer = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE id=$1',
        [
            offerId
        ]
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
    first_offerId = '8'
    second_offerId = '9'

    # act
    await http.request(
        'POST',
        '/api/admin/v1/delete-offer/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offerId': first_offerId,
            'clientId': operator_client
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
            'offerId': second_offerId,
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow(
        'SELECT operator_user_id, status FROM clients WHERE client_id=$1',
        [
            operator_client
        ]
    )
    offers_event_log = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [
            operator_user_id
        ]
    )
    assert offers_event_log[0]['offer_id'] == '8'
    assert offers_event_log[0]['status'] == 'cancelled'
    assert offers_event_log[1]['offer_id'] == '9'
    assert offers_event_log[1]['status'] == 'cancelled'
    assert row_client['operator_user_id'] == 60024649
    assert row_client['status'] == 'waiting'


@pytest.mark.parametrize(
    'method_name',
    [
        'delete-offer',
        'already-published-offer'
    ]
)
async def test_delete_offer__exist_offers_in_progress__client_accepted_if_no_offers_in_progress_and_draft(
        pg,
        method_name,
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
        f'/api/admin/v1/{method_name}/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offerId': offer_in_progress,
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow(
        'SELECT operator_user_id, status FROM clients WHERE client_id=$1',
        [
            operator_client
        ]
    )

    assert row_client['operator_user_id'] == operator_user_id
    assert row_client['status'] == 'accepted'


async def test_update_offers_list__exist_no_client_waiting__returns_no_success(
        pg,
        http,
        offers_and_clients_fixture,
        users_mock,
):
    # arrange
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )

    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute(
        'UPDATE offers_for_call SET status=$1',
        [
            'inProgress'
        ]
    )
    await pg.execute(
        'UPDATE clients SET status=$1',
        [
            'inProgress'
        ]
    )
    operator = 70024649

    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator
        },
        json={},
        expected_status=200
    )

    # assert
    assert not resp.data['success']
    assert resp.data['errors']
    assert resp.data['errors'][0]['code'] == 'offersInProgressExist'


async def test_update_offers_list__exist_no_suitable_client__returns_no_success(
        http,
        users_mock,
):
    # arrange
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )

    operator = 70024649

    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator
        },
        json={},
        expected_status=200
    )

    # assert
    assert not resp.data['success']
    assert resp.data['errors']
    assert resp.data['errors'][0]['code'] == 'suitableClientMissing'


@pytest.mark.parametrize(
    'enable_cleared_priority_filtering',
    [True, False]
)
async def test_update_offers_list__exist_only_invalid_client__returns_no_success(
        http,
        users_mock,
        runtime_settings,
        pg,
        offers_and_clients_fixture,
        parsed_offers_for_offers_and_clients_fixture,
        enable_cleared_priority_filtering,
):
    # arrange
    _CLEAR_PRIORITY = 999999999999999999
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_for_offers_and_clients_fixture)
    # ???????????? ?????? ?????????????? ???? ???????????????? ??????????????????????
    await pg.execute("""
        UPDATE offers_for_call SET priority=$1
    """, [_CLEAR_PRIORITY])
    await runtime_settings.set({
        'ENABLE_CLEARED_PRIORITY_FILTERING': enable_cleared_priority_filtering,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={'roles': []}
        ),
    )
    operator_without_offers_in_progress = 60024636
    # act
    resp = await http.request(
        'POST',
        '/api/admin/v1/update-offers-list/',
        headers={
            'X-Real-UserId': operator_without_offers_in_progress
        },
        json={},
        expected_status=200
    )

    # assert
    assert resp.data['success'] is not enable_cleared_priority_filtering
    assert bool(resp.data['errors']) is enable_cleared_priority_filtering
    if enable_cleared_priority_filtering:
        assert resp.data['errors'][0]['code'] == 'suitableClientMissing'


async def test_call_later_client__operator_and_in_progress__next_call_call_later_priority_set(
        pg,
        http,
        offers_and_clients_fixture,
        runtime_settings
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_client = '1'
    operator = 60024635
    expected_priority = 100000
    expected_next_call = datetime.now(pytz.utc)
    await runtime_settings.set({
        'CALL_LATER_PRIORITY': 1
    })

    # act
    await http.request(
        'POST',
        '/api/admin/v1/call-later-client/',
        headers={
            'X-Real-UserId': operator
        },
        json={
            'clientId': operator_client,
            'callLaterDatetime': expected_next_call.isoformat()
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow(
        'SELECT * FROM clients WHERE client_id=$1',
        [
            operator_client
        ]
    )

    row_offer = await pg.fetchrow(
        'SELECT * FROM offers_for_call WHERE client_id=$1',
        [
            operator_client
        ]
    )

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
            'clientId': operator_client,
            'callLaterDatetime': datetime.now(pytz.utc).isoformat()
        },
        expected_status=200
    )

    # assert
    row_offer_expected_call_later = await pg.fetchrow(
        'SELECT status FROM offers_for_call WHERE id=$1',
        [
            offer_expected_call_later
        ]
    )
    row_offer_expected_cancelled = await pg.fetchrow(
        'SELECT status FROM offers_for_call WHERE id=$1',
        [
            offer_expected_cancelled
        ]
    )
    offers_event_log = await pg.fetch(
        'SELECT * FROM event_log where operator_user_id=$1',
        [
            operator_user_id
        ]
    )

    assert row_offer_expected_call_later['status'] == 'callLater'
    assert row_offer_expected_cancelled['status'] == 'cancelled'
    assert offers_event_log[0]['status'] == 'callLater'
    assert offers_event_log[1]['status'] == 'callLater'
    offers_event_log_ids = [i['offer_id'] for i in offers_event_log]
    assert '10' in offers_event_log_ids
    assert '6' in offers_event_log_ids
    assert len(offers_event_log_ids) == 2


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
            'offerId': offer_in_progress,
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    row_client = await pg.fetchrow(
        'SELECT operator_user_id, status FROM clients WHERE client_id=$1',
        [
            operator_client
        ]
    )

    assert row_client['operator_user_id'] == operator_user_id
    assert row_client['status'] == 'accepted'


@pytest.mark.parametrize(
    'method_name',
    [
        'decline-client',
        'call-missed-client',
        'call-later-client',
        'delete-offer',
        'call-interrupted-client',
        'phone-unavailable-client',
        'promo-given-client',
        'already-published-offer'
    ]
)
async def test_call_offer_list_client_method__missing_client__return_error(
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
            'offerId': offer_in_progress,
            'clientId': operator_client,
            'callLaterDatetime': datetime.now(pytz.utc).isoformat()
        },
        expected_status=200
    )

    # assert
    assert response.data['errors'] == [
        {
            'message': '???????????????????????? ?? ???????????????????? ?????????????????????????????? ???? ????????????',
            'code': 'missingUser'
        }
    ]


@pytest.mark.parametrize(
    'method_name',
    [
        'delete-offer',
        'already-published-offer'
    ]
)
async def test_call_offer_list_offer_method__missing_offer__return_error(
        http,
        method_name,
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
        f'/api/admin/v1/{method_name}/',
        headers={
            'X-Real-UserId': operator_user_id
        },
        json={
            'offerId': offer_in_progress,
            'clientId': operator_client
        },
        expected_status=200
    )

    # assert
    assert response.data['errors'] == [
        {
            'message': '???????????????????? ?? ???????????????????? ?????????????????????????????? ???? ??????????????',
            'code': 'missingOffer'
        }
    ]
