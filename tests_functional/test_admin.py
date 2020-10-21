async def test_get_admin_external_offers_without_x_real_userid(http):
    await http.request('GET', '/admin/external_offers/', expected_status=400)


async def test_get_admin_external_offers_operator_with_client_in_progress(
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
        '/admin/external_offers/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200)

    # assert
    assert resp.body.decode('utf-8') == admin_external_offers_operator_with_client_in_progress_html


async def test_get_admin_external_offers_operator_with_client_cancelled(
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
        '/admin/external_offers/',
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
        '/admin/external_offers/',
        headers={
            'X-Real-UserId': operator_without_clients
        },
        expected_status=200)

    # assert
    assert resp.body.decode('utf-8') == admin_external_offers_operator_without_client_html
