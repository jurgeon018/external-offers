import json

from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_calls_history__create_csv_report(
        http,
        pg,
        offers_and_clients_fixture,
        moderation_confidence_index_mock,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_client = 60024635
    await moderation_confidence_index_mock.add_stub(
        method='POST',
        path='/api/call-component/v1/operator-calls/create-csv-report',
        response=MockResponse(
            body={
                'reportId': '5197d59f-0457-4c46-82b1-59f727c60359',
            },
        ),
    )

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/create-csv-report/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        json={
            'page': 1,
            'operatorId': 123,
            'timeFrom': '2021-12-12T12:12',
            'timeTo': '2022-12-12T12:12',
            'durationMin': 20,
            'durationMax': 40,
        },
        expected_status=200
    )
    body = json.loads(response.body)

    # assert
    assert body['reportId']


async def test_calls_history__get_csv_report_status(
        http,
        pg,
        offers_and_clients_fixture,
        moderation_confidence_index_mock,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_client = 60024635
    await moderation_confidence_index_mock.add_stub(
        method='POST',
        path='/api/call-component/v1/operator-calls/get-csv-report-status',
        response=MockResponse(
            body={
                'status': 'in_progress',
                'url': 'http://test.com'
            },
        ),
    )

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/get-csv-report-status/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        json={'reportId': '5197d59f-0457-4c46-82b1-59f727c60359'},
        expected_status=200
    )
    body = json.loads(response.body)

    # assert
    assert body['status'] == 'inProgress'
