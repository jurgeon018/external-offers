import pytest


async def test_get_offer_card__without_x_real_userid__returns_400(http):
    # act && assert
    await http.request('GET', '/admin/offer-card/1/', expected_status=400)


@pytest.mark.html
async def test_get_offer_card__operator_with_anothers_offer__returns_offer_not_found_message(
        http,
        pg,
        offers_and_clients_fixture,
        parsed_offers_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    operator_with_client = 60024635
    offer_of_another_operator_id = 3

    # act
    resp = await http.request(
        'GET',
        f'/admin/offer-card/{offer_of_another_operator_id}/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200)

    # assert
    assert 'Объявление в работе не найдено' in resp.body.decode('utf-8')


@pytest.mark.html
async def test_get_offer_card__operator_with_offer_declined__returns_offer_not_found_message(
        http,
        pg,
        offers_and_clients_fixture,
        parsed_offers_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    operator_with_client = 60024638
    offer_of_another_operator_id = 7

    # act
    resp = await http.request(
        'GET',
        f'/admin/offer-card/{offer_of_another_operator_id}/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200)

    # assert
    assert 'Объявление в работе не найдено' in resp.body.decode('utf-8')


@pytest.mark.html
async def test_get_offer_card__operator_with_offer_declined__returns_offer_not_found_message(
        http,
        pg,
        offers_and_clients_fixture,
        parsed_offers_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    operator_with_client = 60024638
    offer_of_another_operator_id = 7

    # act
    resp = await http.request(
        'GET',
        f'/admin/offer-card/{offer_of_another_operator_id}/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200)

    # assert
    assert 'Объявление в работе не найдено' in resp.body.decode('utf-8')


@pytest.mark.html
async def test_get_offer_card__operator_with_offer_in_progress__doesnt_return_offer_not_found_message(
        http,
        pg,
        offers_and_clients_fixture,
        parsed_offers_fixture
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    operator_with_client = 60024638
    offer_of_another_operator_id = 6

    # act
    resp = await http.request(
        'GET',
        f'/admin/offer-card/{offer_of_another_operator_id}/',
        headers={
            'X-Real-UserId': operator_with_client
        },
        expected_status=200)

    # assert
    assert 'Объявление в работе не найдено' not in resp.body.decode('utf-8')
