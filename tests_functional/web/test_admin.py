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
    assert operator_without_offers_in_progress == await pg.fetchval('SELECT operator_user_id FROM clients '
                                                                    'WHERE client_id=$1',
                                                                    [expected_operator_client])

    assert expected_operator_offer == await pg.fetchval("SELECT id FROM offers_for_call "
                                                        "WHERE client_id=$1 AND status = 'inProgress'",
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
