from cian_json import json


async def test_save_offer__without_x_real_userid__returns_400(http):
    # act && assert
    await http.request('POST', '/api/admin/v1/save-offer/', expected_status=400)


async def test_save_offer__correct_json__status_ok(http):
    # arrange
    request = {
        'deal_type': 'rent',
        'offer_type': 'flat',
        'category': '',
        'address': 'ул. просторная 6, квартира 200',
        'realty_type': 'apartments',
        'total_area': 120,
        'rooms_count': None,
        'floor_number': 1,
        'floors_count': 5,
        'price': 100000,
        'sale_type': '',
        'phone_number': '89134488338',
        'recovery_password': False
    }
    user_id = 123123

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'ok'


async def test_save_offer__correct_json__offer_status_changed_to_draft(http, pg):
    # arrange
    pg.execute(
        """
        INSERT INTO public.offers_for_call(
            id,
            parsed_id,
            client_id,
            status,
            created_at,
            started_at,
            synced_at
        ) VALUES (
            1,
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '1',
            'inProgress',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )
    request = {
        'deal_type': 'rent',
        'offer_type': 'flat',
        'category': '',
        'address': 'ул. просторная 6, квартира 200',
        'realty_type': 'apartments',
        'total_area': 120,
        'rooms_count': None,
        'floor_number': 1,
        'floors_count': 5,
        'price': 100000,
        'sale_type': '',
        'phone_number': '89134488338',
        'recovery_password': False,

    }
    user_id = 123123

    # act
    await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    status = pg.fetchval("""SELECT status FROM offers_for_call WHERE offer_id='ddd86dec-20f5-4a70-bb3a-077b2754dfe6'""")
    assert status == 'draft'



async def test_save_offer__create_user_by_phone_failed__status_registration_failed(http):
    # arrange
    request = {
        'deal_type': 'rent',
        'offer_type': 'flat',
        'category': '',
        'address': 'ул. просторная 6, квартира 200',
        'realty_type': 'apartments',
        'total_area': 120,
        'rooms_count': None,
        'floor_number': 1,
        'floors_count': 5,
        'price': 100000,
        'sale_type': '',
        'phone_number': '89134488338',
        'recovery_password': False
    }
    user_id = 123123

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'ok'


async def test_save_offer__geocode_failed__status_geocode_failed(http):
    # arrange
    request = {
        'deal_type': 'rent',
        'offer_type': 'flat',
        'category': '',
        'address': 'ул. просторная 6, квартира 200',
        'realty_type': 'apartments',
        'total_area': 120,
        'rooms_count': None,
        'floor_number': 1,
        'floors_count': 5,
        'price': 100000,
        'sale_type': '',
        'phone_number': '89134488338',
        'recovery_password': False
    }
    user_id = 123123

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'geocode_failed'


async def test_save_offer__promo_apply_failed__status_promo_activation_failed(http):
    # arrange
    request = {
        'deal_type': 'rent',
        'offer_type': 'flat',
        'category': '',
        'address': 'ул. просторная 6, квартира 200',
        'realty_type': 'apartments',
        'total_area': 120,
        'rooms_count': None,
        'floor_number': 1,
        'floors_count': 5,
        'price': 100000,
        'sale_type': '',
        'phone_number': '89134488338',
        'recovery_password': False
    }
    user_id = 123123

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'promo_activation_failed'


async def test_save_offer__announcements_draft_failed__status_draft_failed(http):
    # arrange
    request = {
        'deal_type': 'rent',
        'offer_type': 'flat',
        'category': '',
        'address': 'ул. просторная 6, квартира 200',
        'realty_type': 'apartments',
        'total_area': 120,
        'rooms_count': None,
        'floor_number': 1,
        'floors_count': 5,
        'price': 100000,
        'sale_type': '',
        'phone_number': '89134488338',
        'recovery_password': False
    }
    user_id = 123123

    # act
    response = await http.request(
        'POST',
        '/api/admin/v1/save-offer/',
        json=request,
        headers={
            'X-Real-UserId': user_id
        }
    )

    # assert
    assert json.loads(response.body)['status'] == 'draft_failed'
