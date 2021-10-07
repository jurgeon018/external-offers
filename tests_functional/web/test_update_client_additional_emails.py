import json

import pytest


@pytest.mark.gen_test
async def test_update_client_additional_emails(
        http,
        pg,
):
    # arrange
    test_operator = 60024640
    client_id = '1'
    additional_emails = 'a@a.ru a@gmail.com'
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
        '/api/admin/v1/update-client-additional-emails/',
        json={
            'clientId': client_id,
            'additionalEmails': additional_emails,
        },
        headers={
            'X-Real-UserId': 1
        }
    )

    # assert
    rows = await pg.fetch('SELECT client_id, additional_emails FROM clients WHERE client_id = $1', client_id)
    assert rows == [{'client_id': client_id, 'additional_emails': additional_emails}]
    data = json.loads(result.body)
    assert data['success'] is True
    assert data['message'] == 'Дополнительные почты были обновлены'
