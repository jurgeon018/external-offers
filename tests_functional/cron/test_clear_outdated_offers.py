import asyncio


async def test_clear_offers__clearing_disabled__clear_nothing(
    pg,
    runtime_settings,
    runner,
    logs
):
    # arrange
    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '2e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_1931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now() - interval '3 day',
            now() - interval '3 day',
            now() - interval '3 day'
        );
        """
    )
    await runtime_settings.set({
        'ENABLE_OUTDATED_OFFERS_CLEARING': False,
    })

    # act
    await runner.run_python_command('clear-outdated-offers-cron')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM parsed_offers WHERE id = '2e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is not None
    assert any(['Очистка устаревших объявлений отключена' in line
                for line in logs.get_lines()])


async def test_clear_offers__none_updated_in_window__clear_nothing(
    pg,
    runtime_settings,
    runner,
    logs
):
    # arrange
    await runtime_settings.set({
        'ENABLE_OUTDATED_OFFERS_CLEARING': True,
        'ENABLE_WAS_UPDATE_CHECK': True,
        'OFFER_UPDATE_CHECK_WINDOW_IN_HOURS': 24
    })

    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '2e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_1931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now() - interval '3 day',
            now() - interval '3 day',
            now() - interval '3 day'
        );
        """
    )

    # act
    await runner.run_python_command('clear-outdated-offers-cron')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM parsed_offers WHERE id = '2e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is not None
    assert any(['Очистка устаревших объявлений не была запущена из-за отстутствия обновлений' in line
                for line in logs.get_lines()])


async def test_clear_offers__none_updated_in_window_but_check_disabled__clear(
    pg,
    runtime_settings,
    runner,
    logs
):
    # arrange
    await runtime_settings.set({
        'ENABLE_OUTDATED_OFFERS_CLEARING': True,
        'ENABLE_WAS_UPDATE_CHECK': False,
        'OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS': 1
    })

    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '2e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_1931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now() - interval '3 day',
            now() - interval '3 day',
            now() - interval '3 day'
        );
        """
    )

    # act
    await runner.run_python_command('clear-outdated-offers-cron')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM parsed_offers WHERE id = '2e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is None
    assert any(['Проверка наличия обновления отключена' in line
                for line in logs.get_lines()])


async def test_clear_offers__none_before_border__clear_nothing(
    pg,
    runtime_settings,
    runner,
):
    # arrange
    await runtime_settings.set({
        'ENABLE_OUTDATED_OFFERS_CLEARING': True,
        'ENABLE_WAS_UPDATE_CHECK': True,
        'OFFER_UPDATE_CHECK_WINDOW_IN_HOURS': 24,
        'OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS': 4
    })

    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '2e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_1931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now() - interval '3 day',
            now() - interval '3 day',
            now() - interval '3 day'
        );
        """
    )

    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '3e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_2931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now(),
            now(),
            now()
        );
        """
    )

    # act
    await runner.run_python_command('clear-outdated-offers-cron')
    await asyncio.sleep(1)

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM parsed_offers WHERE id = '2e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is not None


async def test_clear_offers__exist_offer_before_border__clear_only(
    pg,
    runtime_settings,
    runner,
):
    # arrange
    await runtime_settings.set({
        'ENABLE_OUTDATED_OFFERS_CLEARING': True,
        'ENABLE_WAS_UPDATE_CHECK': True,
        'OFFER_UPDATE_CHECK_WINDOW_IN_HOURS': 24,
        'OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS': 2
    })

    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '2e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_1931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now() - interval '3 day',
            now() - interval '3 day',
            now() - interval '3 day'
        );
        """
    )

    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '3e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_2931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now(),
            now(),
            now()
        );
        """
    )

    # act
    await runner.run_python_command('clear-outdated-offers-cron')
    await asyncio.sleep(1)
    expected_missing = await pg.fetchval(
        """
        SELECT 1 FROM parsed_offers WHERE id = '2e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    expected_exists = await pg.fetchval(
        """
        SELECT 1 FROM parsed_offers WHERE id = '3e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )

    # assert
    assert expected_exists
    assert not expected_missing


async def test_clear_offers__exist_offer_before_border__clear_only_waiting_offers_for_call(
    pg,
    runtime_settings,
    runner,
):
    # arrange
    await runtime_settings.set({
        'ENABLE_OUTDATED_OFFERS_CLEARING': True,
        'ENABLE_WAS_UPDATE_CHECK': False,
        'OFFER_UPDATE_CHECK_WINDOW_IN_HOURS': 24,
        'OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS': 2
    })

    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '2e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_1931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now() - interval '3 day',
            now() - interval '3 day',
            now() - interval '3 day'
        );
        """
    )

    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '3e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_2931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now() - interval '3 day',
            now() - interval '3 day',
            now() - interval '3 day'
        );
        """
    )

    await pg.execute(
        """
        INSERT INTO public.offers_for_call(
            id,
            parsed_id,
            client_id,
            offer_cian_id,
            status,
            created_at,
            started_at,
            synced_at
        ) VALUES (
            '1',
            '2e6c73b8-3057-47cc-b50a-419052da619f',
            '7',
            3,
            'waiting',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )

    await pg.execute(
        """
        INSERT INTO public.offers_for_call(
            id,
            parsed_id,
            client_id,
            offer_cian_id,
            status,
            created_at,
            started_at,
            synced_at
        ) VALUES (
            '2',
            '3e6c73b8-3057-47cc-b50a-419052da619f',
            '7',
            3,
            'draft',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )

    # act
    await runner.run_python_command('clear-outdated-offers-cron')
    await asyncio.sleep(1)
    expected_missing = await pg.fetchval(
        """
        SELECT 1 FROM offers_for_call WHERE id = '1'
        """
    )

    expected_exists = await pg.fetchval(
        """
        SELECT 1 FROM offers_for_call WHERE id = '2'
        """
    )

    # assert
    assert expected_exists
    assert not expected_missing


async def test_clear_offers__offer_cleard__send_message_to_queue(
    pg,
    runtime_settings,
    runner,
    mocker,
    queue_service
):
    # arrange
    queue = await queue_service.make_tmp_queue(
        routing_key='external-offers.offers-reporting.v1.deleted',
    )

    await runtime_settings.set({
        'ENABLE_OUTDATED_OFFERS_CLEARING': True,
        'ENABLE_WAS_UPDATE_CHECK': False,
        'OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS': 1
    })

    await pg.execute(
        """
        INSERT INTO public.parsed_offers (
            id,
            user_segment,
            source_object_id,
            source_user_id, source_object_model,
            is_calltracking,
            "timestamp",
            created_at,
            updated_at
        ) VALUES (
            '2e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_1931442443',
            '48f05f430722c915c498113b16ba0e79',
            '{}',
            false,
            now() - interval '3 day',
            now() - interval '3 day',
            now() - interval '3 day'
        );
        """
    )

    # act
    await runner.run_python_command('clear-outdated-offers-cron')
    await asyncio.sleep(1)
    messages = await queue.get_messages()
    payload = messages[0].payload

    # assert
    assert len(messages) == 1
    assert payload == {
        'operationId': mocker.ANY,
        'date': mocker.ANY,
        'sourceObjectId': '1_1931442443'
    }
