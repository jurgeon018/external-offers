import json


async def test_update_client_real_info__valid_parameters__real_info_is_changed(
    http,
    pg,
    offers_and_clients_fixture,
    parsed_offers_fixture,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    user_id = 1
    client_id = '1'
    client_before_api_call = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id=$1;
        """,
        [client_id, ]
    )
    real_phone = '8 800 555 35 35'
    real_phone_hunted_at = '2022-01-14 04:44:44.794400+00:00'
    real_name = 'Реальное ФИО'
    # # act
    response = await http.request(
        'POST',
        '/api/admin/v1/update-client-real-info/',
        json={
            'clientId': client_id,
            'realPhone': real_phone,
            'realPhoneHuntedAt': real_phone_hunted_at,
            'realName': real_name,
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )
    body = json.loads(response.body.decode('utf-8'))
    client_after_api_call = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id=$1;
        """,
        [client_id, ]
    )
    # assert
    assert body['success'] is True
    assert body['message'] == 'Реальные данные клиента были успешно изменены'
    assert client_before_api_call['real_phone'] is None
    assert client_before_api_call['real_phone_hunted_at'] is None
    assert client_before_api_call['real_name'] is None
    assert client_after_api_call['real_phone'] == real_phone
    assert str(client_after_api_call['real_phone_hunted_at']) == real_phone_hunted_at
    assert client_after_api_call['real_name'] == real_name
