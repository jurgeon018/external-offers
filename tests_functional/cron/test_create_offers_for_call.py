import asyncio
from datetime import datetime, timedelta

import pytz
from cian_functional_test_utils.pytest_plugin import MockResponse


async def test_create_offers__exist_suitable_parsed_offer_with_new_client__creates_waiting_client(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_clients_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_clients_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE avito_user_id = 'c42bb598767308327e1dffbe7241486c'
        """
    )
    assert row['client_phones'] == ['89883325632']
    assert row['segment'] == 'c'
    assert row['status'] == 'waiting'


async def test_create_offers__exist_nonsuitable_parsed_offer_with_new_client__doesnt_create_waiting_client(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_clients_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_clients_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE avito_user_id = '25f05f430722c915c498113b16ba0e78'
        """
    )
    assert row is None


async def test_create_offers__exist_suitable_parsed_offer__creates_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row['status'] == 'waiting'
    assert row['parsed_created_at'] == datetime(2020, 10, 27, 11, 59, 1, 123093, tzinfo=pytz.utc)


async def test_create_offers__exist_old_offer_and_clear_enabled__clears_waiting_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
        'ENABLE_CLEAR_OLD_WAITING_OFFERS_FOR_CALL': True,

    })

    created_at = datetime.now(pytz.utc) - timedelta(weeks=3)
    await pg.execute(
        """
        INSERT INTO public.offers_for_call (
            id,
            parsed_id,
            client_id,
            status,
            created_at,
            parsed_created_at,
            started_at,
            synced_at,
            priority,
            last_call_id
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        """,
        ['1', 'ddd86dec-20f5-4a70-bb3a-077b2754dfe6', '1',
         'waiting', created_at, created_at, None,
         created_at, 1, None]
    )

    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = 'ddd86dec-20f5-4a70-bb3a-077b2754dfe6'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_with_non_suitable_regions__doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4530],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_with_nonsuitable_segment___doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '575ff03a-573c-4bac-8599-28f17e68a0d8'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_with_nonsuitable_category___doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['suburbanSale'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_without_phones__doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '2e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_with_calltracking__doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )


    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '7b6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_synced__doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '126c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_suitable_parsed_offer_with_existing_client__created_offer_inherited_client_status(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['5', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'inProgress']
    )
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '894ff03a-573c-4bac-8599-28f17e68a0d8'
        """
    )
    assert row['status'] == 'inProgress'


async def test_create_offers__exist_suitable_parsed_offer_with_declined_client__doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['5', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'declined']
    )
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '894ff03a-573c-4bac-8599-28f17e68a0d8'
        """
    )
    assert row is None


async def test_create_offers__exist_suitable_parsed_offer_with_accepted_client__doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        """,
        ['5', '555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'accepted']
    )
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '894ff03a-573c-4bac-8599-28f17e68a0d8'
        """
    )
    assert row is None


async def test_create_offers__exist_suitable_parsed_offer_with_timestamp_before_last_sync_date__doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    offers_and_clients_fixture,
    users_mock
):
    await pg.execute_scripts([parsed_offers_fixture_for_offers_for_call_test, offers_and_clients_fixture])
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '996c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_suitable_parsed_offer_with_suitable_minimum_user_offers__creates_offers(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 3,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    rows = await pg.fetch(
        """
        SELECT * FROM offers_for_call WHERE parsed_id IN ('1d6c73b8-3057-47cc-b50a-419052da619f',
                                                          '2d6c73b8-3057-47cc-b50a-419052da619f',
                                                          '3d6c73b8-3057-47cc-b50a-419052da619f')
        """
    )

    assert len(rows) == 3


async def test_create_offers__exist_nonsuitable_parsed_offer_without_minimum_user_offers__doesnt_create_offers(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 4,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_nonsuitable_parsed_offer_with_maximum_exceeded__doesnt_create_offers(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 1,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 2,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_with_empty_phone__doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    users_mock
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_MINIMUM_OFFERS': 0,
        'OFFER_TASK_CREATION_MAXIMUM_OFFERS': 5,
    })
    await users_mock.add_stub(
        method='GET',
        path='/v2/get-users-by-phone/',
        response=MockResponse(
            body={'users': []}
        ),
    )

    # act
    await runner.run_python_command('create-offers-for-call')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '3e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None
