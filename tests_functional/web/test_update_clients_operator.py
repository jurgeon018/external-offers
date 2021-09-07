import json


async def test_update_clients_operator__valid_parameters__operator_is_changed(
    http,
    pg,
):
    # arrange
    user_id = 1
    operator_1 = 70024649
    operator_2 = 60024653
    operator_3 = 60024659
    operator_4 = 60024660
    await pg.execute(f"""
    INSERT INTO public.clients(
        operator_user_id,client_id,avito_user_id,client_name,client_phones,client_email,status,calls_count,last_call_id
    ) VALUES
    ({operator_1}, '1', '321313', 'Клиент 1', '{{+79812333234}}', 'email4@gmail.com', 'inProgress', 1, NULL),
    ({operator_2}, '2', '321313', 'Клиент 2', '{{+79812333235}}', 'email2@gmail.com', 'waiting', 0, NULL),
    ({operator_3}, '3', '321313', 'Клиент 2', '{{+79812333236}}', 'email2@gmail.com', 'waiting', 0, NULL),
    ({operator_3}, '4', '321313', 'Клиент 2', '{{+79812333237}}', 'email2@gmail.com', 'waiting', 0, NULL),
    ({operator_3}, '5', '321313', 'Клиент 2', '{{+79812333237}}', 'email2@gmail.com', 'inProgress', 1, NULL),
    ({operator_3}, '6', '321313', 'Клиент 1', '{{+79812333238}}', 'email2@gmail.com', 'inProgress', 1, NULL),
    ({operator_1}, '7', '321313', 'Клиент 1', '{{+79812932338}}', 'gmail@gmail.com', 'inProgress', 1, 'last-call-id'),
    ({operator_1}, '8', '321313', 'Клиент 1', '{{+79812932338}}', 'gmail@gmail.com', 'waiting', 1, 'last-call-id');
    """)

    clients_before_api_call = await pg.fetch('SELECT operator_user_id FROM clients;')
    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/update-clients-operator/',
        json={
            'oldOperatorId': operator_1,
            'newOperatorId': operator_4,
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )
    clients_after_api_call = await pg.fetch('SELECT operator_user_id FROM clients;')
    body = json.loads(response.body.decode('utf-8'))
    clients_before_api_call_list = [i['operator_user_id'] for i in clients_before_api_call]
    clients_after_api_call_list = [i['operator_user_id'] for i in clients_after_api_call]

    # assert
    assert body['success'] is True
    assert body['message'] == f'Задания оператора "{operator_1}", были переданы оператору "{operator_4}".'

    # проверяет что поменялись значения тех операторов которые были переданы в ручку
    assert clients_before_api_call_list.count(operator_1) == 3
    assert clients_before_api_call_list.count(operator_4) == 0
    assert clients_after_api_call_list.count(operator_1) == 0
    assert clients_after_api_call_list.count(operator_4) == 3

    # остальные значения не поменялись
    assert clients_before_api_call_list.count(operator_2) == 1
    assert clients_before_api_call_list.count(operator_3) == 4
    assert clients_after_api_call_list.count(operator_2) == 1
    assert clients_after_api_call_list.count(operator_3) == 4
