import json


async def test_update_offer_comment__valid_parameters__comment_is_changed(
    http,
    pg,
    offers_and_clients_fixture,
    parsed_offers_fixture,
):
    # arrange
    await pg.execute_scripts(offers_and_clients_fixture)
    await pg.execute_scripts(parsed_offers_fixture)
    offer_id = '1'
    comment = 'comment text'
    user_id = 1
    comment_before_api_call = await pg.fetchval(
        """
        SELECT comment FROM offers_for_call WHERE id=$1;
        """,
        [offer_id, ]
    )
    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/update-offer-comment/',
        json={
            'offerId': offer_id,
            'comment': comment,
        },
        headers={
            'X-Real-UserId': user_id
        },
        expected_status=200
    )

    comment_after_api_call = await pg.fetchval(
        """
        SELECT comment FROM offers_for_call WHERE id=$1;
        """,
        [offer_id, ]
    )
    body = json.loads(response.body.decode('utf-8'))

    # assert
    assert body['success'] is True
    assert body['message'] == 'Коментарий к обьявлению был успешно обновлен.'
    assert comment_after_api_call != comment_before_api_call
    assert comment_after_api_call == comment
