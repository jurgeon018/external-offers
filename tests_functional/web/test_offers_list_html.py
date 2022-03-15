import os
import re

import pytest
from cian_functional_test_utils.pytest_plugin import MockResponse


@pytest.mark.html
async def test_get_offers_list__operator_with_client_in_progress__returns_offers_in_progress_page(
        http,
        pg,
        admin_external_offers_operator_with_client_in_progress_html,
        offers_and_clients_fixture,
        users_mock
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_client = 60024635
    stub = await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={
                'roles': [],
            },
        ),
    )

    # act
    resp = await http.request(
        'GET',
        '/admin/offers-list/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200
    )

    html = resp.body.decode('utf-8')
    html_without_dynamic_datetime = re.sub(
        r'<input id="call-later-datetime" type="datetime-local" value=([\d\:\-T]*)>',
        '',
        html
    )
    html_without_dynamic_datetime = re.sub(
        (
            r'<input type="datetime-local" id="realPhoneDtInput" '
            r'placeholder="Введите дату добычи реального номера телефона" '
            r'value=([\d\:\-T]*) size=30>'
        ),
        '',
        html_without_dynamic_datetime
    )

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_with_client_in_progress_html.write_text(html_without_dynamic_datetime)

    # assert
    assert html_without_dynamic_datetime == (admin_external_offers_operator_with_client_in_progress_html
                                             .read_text('utf-8'))


@pytest.mark.html
async def test_get_offers_list__operator_with_client_cancelled__returns_no_offers_page(
        http,
        pg,
        offers_and_clients_fixture,
        parsed_offers_for_offers_and_clients_fixture,
        admin_external_offers_operator_with_client_cancelled_html,
        users_mock,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_for_offers_and_clients_fixture)

    operator_with_client = 60024636
    stub = await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={
                'roles': [],
            },
        ),
    )

    # act
    resp = await http.request(
        'GET',
        '/admin/offers-list/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200
    )

    html = resp.body.decode('utf-8')
    html_without_dynamic_datetime = re.sub(
        r'<input id="call-later-datetime" type="datetime-local" value=([\d\:\-T]*)>',
        '',
        html
    )
    html_without_dynamic_datetime = re.sub(
        (
            r'<input type="datetime-local" id="realPhoneDtInput" '
            r'placeholder="Введите дату добычи реального номера телефона" '
            r'value=([\d\:\-T]*) size=30>'
        ),
        '',
        html_without_dynamic_datetime
    )

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_with_client_cancelled_html.write_text(html_without_dynamic_datetime)

    # assert
    assert html_without_dynamic_datetime == (admin_external_offers_operator_with_client_cancelled_html
                                             .read_text('utf-8'))


@pytest.mark.html
async def test_get_offers__operator_without_client__returns_no_offers_page(
        pg,
        http,
        admin_external_offers_operator_without_client_html,
        offers_and_clients_fixture,
        parsed_offers_for_offers_and_clients_fixture,
        users_mock,
):
    # arrange
    await pg.execute_scripts(parsed_offers_for_offers_and_clients_fixture)
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_without_clients = 1
    stub = await users_mock.add_stub(
        method='GET',
        path='/v1/get-user-roles/',
        response=MockResponse(
            body={
                'roles': [],
            },
        ),
    )

    # act
    resp = await http.request(
        'GET',
        '/admin/offers-list/',
        headers={
            'X-Real-UserId': operator_without_clients
        },
        expected_status=200
    )

    html = resp.body.decode('utf-8')
    html_without_dynamic_datetime = re.sub(
        r'<input id="call-later-datetime" type="datetime-local" value=([\d\:\-T]*)>',
        '',
        html
    )
    html_without_dynamic_datetime = re.sub(
        (
            r'<input type="datetime-local" id="realPhoneDtInput" '
            r'placeholder="Введите дату добычи реального номера телефона" '
            r'value=([\d\:\-T]*) size=30>'
        ),
        '',
        html_without_dynamic_datetime
    )

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_without_client_html.write_text(html_without_dynamic_datetime)

    # assert
    assert html_without_dynamic_datetime == (admin_external_offers_operator_without_client_html
                                             .read_text('utf-8'))
