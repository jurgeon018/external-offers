import json


async def test_update_client_reason_of_decline(
        http,
        pg,
):
    # arrange
    test_operator = 60024640
    client_id = '1'
    reason_of_decline = 'decline_conversation'
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
        ['1', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', test_operator, 'inProgress']
    )

    # act
    result = await http.request(
        'POST',
        '/api/admin/v1/update-client-reason-of-decline/',
        json={
            'clientId': client_id,
            'reasonOfDecline': reason_of_decline,
        },
        headers={
            'X-Real-UserId': 1
        }
    )

    # assert
    rows = await pg.fetch('SELECT client_id, reason_of_decline FROM clients WHERE client_id = $1', client_id)
    assert rows == [{'client_id': client_id, 'reason_of_decline': reason_of_decline}]
    data = json.loads(result.body)
    assert data['success'] is True
    assert data['message'] == 'Причина отказа была обновлена'
