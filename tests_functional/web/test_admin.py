from cian_json import json


async def test_get_admin_offers_list_without_x_real_userid(http):
    await http.request('GET', '/admin/offers-list/', expected_status=400)


async def test_get_admin_offers_list_operator_with_client_in_progress(
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

    # assert
    assert resp.body.decode('utf-8') == admin_external_offers_operator_with_client_in_progress_html


async def test_get_admin_offers_list_operator_with_client_cancelled(
        http,
        pg,
        offers_and_clients_fixture,
        admin_external_offers_operator_with_client_cancelled,
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

    # assert
    assert resp.body.decode('utf-8') == admin_external_offers_operator_with_client_cancelled


async def test_admin_operator_without_client(
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

    # assert
    assert resp.body.decode('utf-8') == admin_external_offers_operator_without_client_html


async def test_post_update_offers_list_operator_with_in_progress_not_success(
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
        '/admin/update-offers-list/',
        headers={
            'X-Real-UserId': operator_with_offers_in_progress
        },
        expected_status=200)

    # assert
    assert not resp.data['success']
    assert resp.data['errors']


async def test_post_update_offers_list_operator_without_client_success(
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
        '/admin/update-offers-list/',
        headers={
            'X-Real-UserId': operator_without_offers_in_progress
        },
        expected_status=200)

    # assert
    assert resp.data['success']
    assert not resp.data['errors']


async def test_post_update_offers_list_operator_without_client_updates_non_success(
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
        '/admin/update-offers-list/',
        headers={
            'X-Real-UserId': operator_without_offers_in_progress
        },
        expected_status=200)

    # assert

    assert resp.data['success']
    assert not resp.data['errors']


async def test_post_first_update_offers_list_operator_without_client_updates_first_created(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_without_offers_in_progress = 60024636
    expected_operator_client = 3
    expected_operator_offer = 4
    # act
    await http.request(
        'POST',
        '/admin/update-offers-list/',
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


async def test_post_second_update_offers_list_operator_without_client_updates_second_created(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    first_operator_without_offers_in_progress = 60024636
    second_operator_without_offers_in_progress = 60024637
    expected_operator_client = 2
    expected_operator_offer = 5

    # act
    await http.request(
        'POST',
        '/admin/update-offers-list/',
        headers={
            'X-Real-UserId': first_operator_without_offers_in_progress
        },
        expected_status=200)

    await http.request(
        'POST',
        '/admin/update-offers-list/',
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


async def test_post_declined_client_no_operator_and_status_declined(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator = 60024636
    operator_client = 2

    # act
    await http.request(
        'POST',
        '/admin/decline-client/',
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
    assert row_client['status'] == 'declined'


async def test_post_declined_client_offers_in_progress_set_declined(
        pg,
        http,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator = 60024636
    operator_client = 4
    offer_expected_declined = 6
    offer_expected_cancelled = 7

    # act
    await http.request(
        'POST',
        '/admin/decline-client/',
        headers={
            'X-Real-UserId': operator
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

    assert row_offer_expected_declined['status'] == 'declined'
    assert row_offer_expected_cancelled['status'] == 'cancelled'


async def test_save_offer_without_x_real_userid(http):
    await http.request('POST', '/api/admin/v1/save-offer/', expected_status=400)


async def test_save_offer(http):
    # arrange
    request = {
        'deal_type': 'rent',
        'offer_type': 'flat',
        'category': '',
        'address': 'ул. просторная 6, квартира 200',
        'realty_type': 'apartments',
        'total_area': 120,
        'rooms_count': None,
        'floor_number': 1,
        'floors_count': 5,
        'price': 100000,
        'sale_type': "",
        'phone_number': '89134488338',
        'recovery_password': False
    }
    user_id = 123123

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'ok'
