import json

async def test_update_client_comment__valid_parameters__comment_is_changed(
    http,
    pg,
    offers_and_clients_fixture,
    parsed_offers_fixture,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    client_id = "1"
    comment = "comment text"
    user_id = 1
    comment_before_api_call = await pg.fetchval(
        """
        SELECT comment FROM clients WHERE client_id=$1;
        """,
        [client_id, ]
    )
    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/update-client-comment/',
        json={
            'clientId': client_id,
            'comment': comment,
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )

    comment_after_api_call = await pg.fetchval(
        """
        SELECT comment FROM clients WHERE client_id=$1;
        """,
        [client_id, ]
    )
    body = json.loads(response.body.decode('utf-8'))

    # assert
    assert body['success'] is True
    assert body['message'] == 'Коментарий к карточке клиента был обновлен.'
    assert comment_after_api_call != comment_before_api_call
    assert comment_after_api_call == comment


async def test_update_client_comment__client_doesnt_exist__comment_is_not_changed(
    http,
    pg,
    offers_and_clients_fixture,
    parsed_offers_fixture,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    client_id = "0"
    comment = "comment text"
    user_id = 1
    get_client_sql = """
    SELECT comment FROM clients WHERE client_id=$1;
    """, [client_id, ]
    comment_before_api_call = await pg.fetchval(*get_client_sql)
    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/update-client-comment/',
        json={
            'clientId': client_id,
            'comment': comment,
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )

    comment_after_api_call = await pg.fetchval(*get_client_sql)
    body = json.loads(response.body.decode('utf-8'))

    # assert
    assert body['success'] is False
    assert body['message'] == 'Такого клиента не существует.'
    assert comment_after_api_call == comment_before_api_call
    assert comment_after_api_call != comment
