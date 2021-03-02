async def test_update_client_phone__client_exist__update_client_phone(
        http,
        pg,
):
    # arrange
    expected_client_phone = '+79819548423'
    user_id = 1
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['89134488338'], 'nemoy@gmail.com', user_id, 'inProgress']
    )

    # act
    await http.request(
        'POST',
        '/api/admin/v1/update-client-phone/',
        json={
            'clientId': '7',
            'phoneNumber': expected_client_phone
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )

    client_phones = await pg.fetchval(
        """
        SELECT client_phones FROM clients WHERE client_id = '7'
        """
    )

    # assert
    assert client_phones == [expected_client_phone]
