import asyncio

from cian_functional_test_utils.pytest_plugin import MockResponse
from cian_json import json


async def test_create_test_parsed_offers_and_run_offers_creation_cron(
    pg,
    http,
    runtime_settings,
    users_mock,
):
    # arrange
    await runtime_settings.set({
        'CLEAR_HOMEOWNERS_WITH_EXISTING_ACCOUNTS': False,
        'OFFER_TASK_CREATION_SEGMENTS': ['d'],
        'OFFER_TASK_CREATION_CATEGORIES': [
            'flatSale', 'flatRent', 'officeRent', 'houseRent', 'officeSale', 'houseSale'
        ],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'NO_LK_HOMEOWNER_PRIORITY': 4,
        'WAITING_PRIORITY': 3,
        'HOMEOWNER_PRIORITY': 2,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act

    # # # v1
    # await pg.execute("""
    #     INSERT INTO public.parsed_offers (
    #         id, source_group_id, user_subsegment, user_segment, source_object_id, source_user_id, source_object_model, is_calltracking, "timestamp", created_at, updated_at
    #     ) VALUES (
    #         $1,
    #         'group_id1',
    #         'subsegment1',
    #         'd',
    #         '1_1931552437',
    #         '95f05f430722c915c498113b16ba0e78',
    #         '{"phones": ["89516137979"], "category": "houseSale", "region": 4580, "title": "2-\u043a \u043a\u0432\u0430\u0440\u0442\u0438\u0440\u0430, 52 \u043c\u00b2, 8/9 \u044d\u0442.", "description": "\u041a\u0432\u0430\u0440\u0442\u0438\u0440\u0430 \u0432 \u0445\u043e\u0440\u043e\u0448\u0435\u043c \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0438, \u0443\u043b\u0443\u0447\u0448\u0435\u043d\u043d\u043e\u0439 \u043f\u043b\u0430\u043d\u0438\u0440\u043e\u0432\u043a\u0438, \u043f\u043e \u0443\u043b\u0438\u0446\u0435 \u0412\u0435\u0441\u0435\u043d\u043d\u044f\u044f, \u0440\u0430\u0439\u043e\u043d \u041a\u0440\u0430\u0441\u043d\u043e\u0433\u043e \u043a\u0430\u043c\u043d\u044f. \u0423\u0445\u043e\u0436\u0435\u043d\u043d\u0430\u044f, \u0441\u043e\u043b\u043d\u0435\u0447\u043d\u0430\u044f, \u0434\u0432\u0430 \u0437\u0430\u0441\u0442\u0435\u043a\u043b\u0435\u043d\u043d\u044b\u0445 \u0431\u0430\u043b\u043a\u043e\u043d\u0430! \u0412\u043e \u0432\u0441\u0435\u0439 \u043a\u0432\u0430\u0440\u0442\u0438\u0440\u0435 \u043f\u043b\u0430\u0441\u0442\u0438\u043a\u043e\u0432\u044b\u0435 \u043e\u043a\u043d\u0430, \u043d\u0430 \u043f\u043e\u043b\u0443 \u043b\u0438\u043d\u043e\u043b\u0435\u0443\u043c, \u0434\u043e\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044c\u043d\u043e \u043a\u043b\u0430\u0434\u043e\u0432\u0430\u044f. \u0421\u0430\u043d\u0443\u0437\u0435\u043b \u0440\u0430\u0437\u0434\u0435\u043b\u044c\u043d\u044b\u0439, \u043e\u0442\u0434\u0435\u043b\u043a\u0430 \u0441\u0442\u0435\u043d \u043a\u0430\u0444\u0435\u043b\u0435\u043c, \u0441\u0430\u043d\u0442\u0435\u0445\u043d\u0438\u043a\u0430 \u0432 \u0445\u043e\u0440\u043e\u0448\u0435\u043c \u0441\u043e\u0441\u0442\u043e\u044f\u043d\u0438\u0438. \u0412\u0445\u043e\u0434\u043d\u0430\u044f \u0434\u0432\u0435\u0440\u044c \u0435\u0432\u0440\u043e. \u0420\u044f\u0434\u043e\u043c \u0441 \u0434\u043e\u043c\u043e\u043c \u0432\u0441\u044f \u0438\u043d\u0444\u0440\u0430\u0441\u0442\u0440\u0443\u043a\u0442\u0443\u0440\u0430.\u0420\u0430\u0441\u0441\u043c\u0430\u0442\u0440\u0438\u0432\u0430\u0435\u043c \u0432\u0441\u0435 \u0432\u0438\u0434\u044b \u0440\u0430\u0441\u0447\u0451\u0442\u0430, \u043f\u043e\u043c\u043e\u0436\u0435\u043c \u0441 \u043e\u0444\u043e\u0440\u043c\u043b\u0435\u043d\u0438\u0435\u043c \u0438\u043f\u043e\u0442\u0435\u043a\u0438.", "address": "\u041a\u0435\u043c\u0435\u0440\u043e\u0432\u0441\u043a\u0430\u044f \u043e\u0431\u043b\u0430\u0441\u0442\u044c, \u041a\u0438\u0441\u0435\u043b\u0435\u0432\u0441\u043a\u0438\u0439 \u0433.\u043e., \u041a\u0438\u0441\u0435\u043b\u0435\u0432\u0441\u043a, \u0412\u0435\u0441\u0435\u043d\u043d\u044f\u044f \u0443\u043b., 16"}',
    #         false,
    #         '2020-10-26 16:55:00+03',
    #         '2020-10-27 14:59:01.123093+03',
    #         '2020-10-27 15:20:02.708205+03'
    #     )
    # """, [parsed_id])
    # # # v2
    result = await http.request(
        'POST',
        '/api/admin/v1/create-test-parsed-offer/',
        json={
            # 'id': '123',
            # 'id': '9d6c73b8-3057-47cc-b50a-419052da619f',
            # 'id': parsed_id,
            'sourceObjectId': '1_1931552437',
            'sourceUserId': '95f05f430722c915c498113b16ba0e78',
            'isCalltracking': False,
            'userSegment': 'd',
            'userSubsegment': 'subsegment1',
            'sourceGroupId': 'group_id1',
            'externalOfferType': None,
            # source_object_model
            'phone': '89516137979',
            'category': 'houseSale',
            'title': 'Название обьявки',
            'address': 'Адрес',
            'region': 4580,
            'price': None,
            'priceType': None,
            'contact': None,
            'totalArea': None,
            'floorNumber': None,
            'floorsCount': None,
            'roomsCount': None,
            'url': None,
            'isAgency': None,
            'isDeveloper': None,
            'isStudio': None,
            'town': None,
            'lat': None,
            'lng': None,
            'livingArea': None,
            'description': None,
        },
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    resp = json.loads(result.body.decode('utf-8'))
    parsed_id = resp['parsedId']

    # # # v1
    # await run cron
    # # # v2
    result = await http.request(
        'POST',
        '/api/admin/v1/create-test-offers-for-call/',
        headers={
            'X-Real-UserId': 1
        },
        expected_status=200
    )
    await asyncio.sleep(2)

    # assert
    offer_row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = $1
        """,
        [parsed_id]
    )

    client_row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE client_id = $1
        """,
        [offer_row['client_id']]
    )
    assert resp['success'] is True
    assert offer_row['status'] == 'waiting'
    assert offer_row['priority'] == 232120412
    assert client_row['cian_user_id'] is None
