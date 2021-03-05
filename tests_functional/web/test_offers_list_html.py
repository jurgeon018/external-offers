import os
import re
import pytest


async def test_get_offers_list__without_x_real_userid__returns_400(http):
    # act && assert
    await http.request('GET', '/admin/offers-list/', expected_status=400)


@pytest.mark.html
async def test_get_offers_list__operator_with_client_in_progress__returns_offers_in_progress_page(
        http,
        pg,
        admin_external_offers_operator_with_client_in_progress_html,
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_client = 60024635

    # act
    resp = await http.request(
        'GET',
        '/admin/offers-list/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200)

    html = resp.body.decode('utf-8')
    html_without_dynamic_datetime = re.sub(
        r'<input id="call-later-datetime" type="datetime-local" value=([\d\:\-T]*)>',
        '',
        html
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
        admin_external_offers_operator_with_client_cancelled_html,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_with_client = 60024636

    # act
    resp = await http.request(
        'GET',
        '/admin/offers-list/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200)

    html = resp.body.decode('utf-8')
    html_without_dynamic_datetime = re.sub(
        r'<input id="call-later-datetime" type="datetime-local" value=([\d\:\-T]*)>',
        '',
        html
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
        offers_and_clients_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    operator_without_clients = 1

    # act
    resp = await http.request(
        'GET',
        '/admin/offers-list/',
        headers={
            'X-Real-UserId': operator_without_clients
        },
        expected_status=200)
    html = resp.body.decode('utf-8')
    html_without_dynamic_datetime = re.sub(
        r'<input id="call-later-datetime" type="datetime-local" value=([\d\:\-T]*)>',
        '',
        html
    )

    if 'UPDATE_HTML_FIXTURES' in os.environ:
        admin_external_offers_operator_without_client_html.write_text(html_without_dynamic_datetime)

    # assert
    assert html_without_dynamic_datetime == (admin_external_offers_operator_without_client_html
                                             .read_text('utf-8'))
