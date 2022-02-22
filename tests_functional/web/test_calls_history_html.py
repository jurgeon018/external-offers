import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse


@pytest.mark.html
@pytest.mark.parametrize('search_params', [
    {},
    {
        'page': 1,
        'operator_id': 123,
        'time_from': '2021-12-12T12:12',
        'time_to': '2022-12-12T12:12',
        'duration_min': 20,
        'duration_max': 40,
    },
    {
        'page': 'qwe',
        'operator_id': 'qwe',
        'time_from': 'qwe',
        'time_to': 'qwe',
        'duration_min': 'qwe',
        'duration_max': 'qwe',
    }
])
async def test_calls_history__return_html_page(
        http,
        pg,
        offers_and_clients_fixture,
        moderation_confidence_index_mock,
        search_params,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_client = 60024635
    await moderation_confidence_index_mock.add_stub(
        method='POST',
        path='/api/call-component/v1/get-operator-calls',
        response=MockResponse(
            body={
                'calls': [
                    {
                        'callId': '5197d59f-0457-4c46-82b1-59f727c60359',
                        'createdTime': '2022-02-09T13:29:12.417306+03:00',
                        'operatorId': operator_with_client,
                        'phoneFrom': '79666663107',
                        'phoneTo': '79312882017',
                        'beepDuration': 7,
                        'duration': 7,
                        'taskKey': 'taskKey1',
                        'team': 'moderation1',
                        'mp3Url': None
                    },
                    {
                        'callId': '5197d59f-0457-4c46-82b1-59f727c60359',
                        'createdTime': '2022-02-09T13:29:12.417306+03:00',
                        'operatorId': operator_with_client,
                        'phoneFrom': '79666663107',
                        'phoneTo': '79312882017',
                        'beepDuration': 7,
                        'duration': 7,
                        'taskKey': 'taskKey1',
                        'team': 'moderation1',
                        'mp3Url': None
                    },
                ],
            },
        ),
    )

    # act
    resp = await http.request(
        'GET',
        '/admin/calls-history/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        params=search_params,
        expected_status=200
    )

    html = resp.body.decode('utf-8')

    # assert
    assert '<!DOCTYPE html>' in html
    assert '79312882017' in html
    assert '79312882017' in html
