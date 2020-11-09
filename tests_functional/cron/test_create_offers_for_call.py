import asyncio


async def test_create_offers__exist_suitable_parsed_offer_with_new_client__creates_waiting_client(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_clients_test
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_clients_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE avito_user_id = 'c42bb598767308327e1dffbe7241486c'
        """
    )
    assert row['client_phones'] == ['89883325632']
    assert row['status'] == 'waiting'


async def test_create_offers__exist_nonsuitable_parsed_offer_with_new_client__doesnt_create_waiting_client(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_clients_test
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_clients_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['c'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM clients WHERE avito_user_id = '25f05f430722c915c498113b16ba0e78'
        """
    )
    assert row is None


async def test_create_offers__exist_suitable_parsed_offer__creates_waiting_offer_for_call(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4580]

    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """)
    assert row['status'] == 'waiting'


async def test_create_offers__exist_parsed_offer_with_non_suitable_regions__doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
        'OFFER_TASK_CREATION_REGIONS': [4530]

    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

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
    parsed_offers_fixture_for_offers_for_call_test
):
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

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
    parsed_offers_fixture_for_offers_for_call_test
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['suburbanSale'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '1d6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_without_phones___doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '2e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_with_calltracking___doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '7b6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_parsed_offer_synced___doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test
):
    # arrange
    await pg.execute_scripts(parsed_offers_fixture_for_offers_for_call_test)
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '126c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None


async def test_create_offers__exist_suitable_parsed_offer_with_existing_client___created_offer_inherited_client_status(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test
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
        ['5','555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'inProgress']
    )
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '894ff03a-573c-4bac-8599-28f17e68a0d8'
        """
    )
    assert row['status'] == 'inProgress'


async def test_create_offers__exist_suitable_parsed_offer_with_declined_client___doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test
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
        ['5','555bb598767308327e1dffbe7241486c', 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'declined']
    )
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '894ff03a-573c-4bac-8599-28f17e68a0d8'
        """
    )
    assert row is None


async def test_create_offers__exist_suitable_parsed_offer_with_timestamp_before_last_sync_date___doesnt_create_offer(
    pg,
    runtime_settings,
    runner,
    parsed_offers_fixture_for_offers_for_call_test,
    offers_and_clients_fixture
):
    await pg.execute_scripts([parsed_offers_fixture_for_offers_for_call_test, offers_and_clients_fixture])
    await runtime_settings.set({
        'OFFER_TASK_CREATION_SEGMENTS': ['b'],
        'OFFER_TASK_CREATION_CATEGORIES': ['flatSale', 'flatRent'],
    })

    # act
    await runner.run_python_command('create-offers-for-call')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM offers_for_call WHERE parsed_id = '996c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None
