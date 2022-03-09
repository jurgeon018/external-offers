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
                'status': 'inProgress',
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


async def test_calls_history__download_csv(
        http,
        pg,
        offers_and_clients_fixture,
        moderation_confidence_index_mock,
):
    # arrange
    content = b'Id\tCreatedTime\tCallId\tStatus\tcall.OperatorId\tSourcePhone\tTargetPhone\tDurationSec\t' \
              b'BeepDurationSec\tTaskKey\tTeam\tMp3Url\n18\t02/17/2022 11:41:35\t' \
              b'dec4798f-1357-48c1-b860-cb2a80a7cd12\tNotConnected\t21257708\t79032241754\t79312882017\t' \
              b'5\t5\tdefault_task_key\tdefault_team\t\n'
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_client = 60024635
    await moderation_confidence_index_mock.add_stub(
        method='GET',
        path='/api/call-component/v1/operator-calls/download-csv-report.csv',
        response=MockResponse(
            body={
                'content': content,
            },
        ),
    )

    # act
    response = await http.request(
        'GET',
        '/api/admin/v1/download_csv/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        params={'reportId': '5197d59f-0457-4c46-82b1-59f727c60359'},
        expected_status=200
    )
    body = json.loads(response.body)

    # assert
    assert body['content'] == content.decode()
