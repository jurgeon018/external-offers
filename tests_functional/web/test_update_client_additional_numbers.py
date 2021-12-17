import json

import pytest


async def test_update_client_additional_numbers(
        http,
        pg,
):
    # arrange
    test_operator = 60024640
    client_id = '1'
    additional_numbers = '+79999999999 +79999991919'
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
        '/api/admin/v1/update-client-additional-numbers/',
        json={
            'clientId': client_id,
            'additionalNumbers': additional_numbers,
        },
        headers={
            'X-Real-UserId': 1
        }
    )

    # assert
    rows = await pg.fetch('SELECT client_id, additional_numbers FROM clients WHERE client_id = $1', client_id)
    assert rows == [{'client_id': client_id, 'additional_numbers': additional_numbers}]
    data = json.loads(result.body)
    assert data['success'] is True
    assert data['message'] == 'Дополнительные тел. номера были обновлены'
