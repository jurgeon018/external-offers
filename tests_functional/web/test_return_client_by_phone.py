async def test_return_client_by_phone__correct_request__client_and_offers_returned(
        http,
        pg,
):
    # arrange
    client_phone = '89134488338'
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
         ['89134488338'], 'nemoy@gmail.com', None, 'callLater']
    )

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
            priority,
            last_call_id
        ) VALUES (
            1,
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            'callMissed',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            1,
            NULL
        ), (
            2,
            'f1a91ade-13a2-48d9-a05a-6131af39033e',
            '7',
            'draft',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            1,
            NULL
        )
        """
    )
    # act
    await http.request(
        'POST',
        '/api/admin/v1/return-client-by-phone/',
        json={
            'phoneNumber': client_phone
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )

    client = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = '7'
        """
    )

    before_return_call_missed_offer = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE id = '1'
        """
    )

    before_return_draft_offer = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE id = '2'
        """
    )

    # assert
    assert client['operator_user_id'] == user_id
    assert client['status'] == 'inProgress'
    assert before_return_call_missed_offer['status'] == 'inProgress'
    assert before_return_call_missed_offer['last_call_id'] is not None
    assert before_return_draft_offer['status'] == 'draft'
    assert before_return_draft_offer['last_call_id'] is None
