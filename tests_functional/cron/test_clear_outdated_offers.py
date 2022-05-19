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

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM parsed_offers WHERE id = '2e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is not None
    assert any(['Очистка устаревших объявлений отключена' in line
                for line in logs.get_lines()])


async def test_clear_offers__new_offers_count_less_than_necessary___clear_nothing(
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
        'ENABLE_OUTDATED_OFFERS_CLEARING': True,
        'ENABLE_WAS_UPDATE_CHECK': False,
        'OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS': 1,
        'NEW_PARSED_OFFERS_COUNT_FOR_DELETE_OLD': 1000,
    })

    # act
    await runner.run_python_command('clear-outdated-offers-cron')

    # assert
    row = await pg.fetchrow(
        """
        SELECT * FROM parsed_offers WHERE id = '2e6c73b8-3057-47cc-b50a-419052da619f'
        """
    )
    assert row is not None
    assert any('Очистка устаревших объявлений не была запущена из-за отстутствия новых объявлений' in line
               for line in logs.get_lines())


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
        'OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS': 1,
        'NEW_PARSED_OFFERS_COUNT_FOR_DELETE_OLD': 0,
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
        'OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS': 2,
        'NEW_PARSED_OFFERS_COUNT_FOR_DELETE_OLD': 0,
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
    kafka_service,
):
    # arrange
    await runtime_settings.set({
        'ENABLE_OUTDATED_OFFERS_CLEARING': True,
        'ENABLE_WAS_UPDATE_CHECK': False,
        'OFFER_UPDATE_CHECK_WINDOW_IN_HOURS': 24,
        'OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS': 2,
        'DELETE_OLD_OFFERS_CHUNK': 1,
        'NEW_PARSED_OFFERS_COUNT_FOR_DELETE_OLD': 0,
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
            '4e6c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_3931442443',
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
            synced_at,
            source_object_id
        ) VALUES (
            '1',
            '2e6c73b8-3057-47cc-b50a-419052da619f',
            '7',
            3,
            'waiting',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '1'
        )
        """
    )
    await pg.execute("""
        INSERT INTO public.clients(
            real_phone,
            real_phone_hunted_at,
            client_id,
            avito_user_id,
            client_phones,
            status,
            synced_with_grafana,
            is_test,
            main_account_chosen,
            unactivated
        ) VALUES (
            NULL,
            NULL,
            '7',
            '7',
            '{1234567}',
            'waiting',
            'f',
            'f',
            'f',
            'f'
        )
    """)
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
            synced_at,
            source_object_id
        ) VALUES (
            '2',
            '3e6c73b8-3057-47cc-b50a-419052da619f',
            '7',
            3,
            'draft',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2'
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
            synced_at,
            source_object_id
        ) VALUES (
            '3',
            '4e6c73b8-3057-47cc-b50a-419052da619f',
            '8',
            4,
            'callLater',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '3'
            )
        """
    )
    await pg.execute("""
        INSERT INTO public.clients(
            real_phone,
            real_phone_hunted_at,
            client_id,
            avito_user_id,
            client_phones,
            status,
            synced_with_grafana,
            is_test,
            main_account_chosen,
            unactivated
        ) VALUES (
            NULL,
            NULL,
            '8',
            '8',
            '{3234567}',
            'callLater',
            'f',
            'f',
            'f',
            'f'
        )
    """)
    await pg.execute("""
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
            '100c73b8-3057-47cc-b50a-419052da619f',
            'b',
            '1_1001442443',
            '10005f430722c915c498113b16ba0e79',
            '{}',
            false,
            now() - interval '3 day',
            now() - interval '3 day',
            now() - interval '3 day'
        );
        INSERT INTO public.offers_for_call(
            id,
            parsed_id,
            client_id,
            offer_cian_id,
            status,
            created_at,
            started_at,
            synced_at,
            source_object_id
        ) VALUES (
            '100',
            '100c73b8-3057-47cc-b50a-419052da619f',
            '100',
            100,
            'waiting',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '4'
        );
        INSERT INTO public.clients(
            real_phone,
            real_phone_hunted_at,
            client_id,
            avito_user_id,
            client_phones,
            status,
            synced_with_grafana,
            is_test,
            main_account_chosen,
            unactivated
        ) VALUES (
            NULL,
            NULL,
            '100',
            '100',
            '{1004567}',
            'waiting',
            'f',
            'f',
            'f',
            'f'
        );
    """)

    # act
    await runner.run_python_command('clear-outdated-offers-cron')
    await kafka_service.wait_messages(
        topic='external-offers.deleted-offers-for-call',
        timeout=2.5,
        count=2,
    )
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

    expected_call_later_exists = await pg.fetchval("""
        SELECT 1 FROM offers_for_call WHERE id = '3'
    """)

    expected_unhunted_missing = await pg.fetchval("""
        SELECT 1 FROM offers_for_call WHERE id = '100'
    """)

    # assert
    assert expected_exists
    assert not expected_missing
    assert expected_call_later_exists
    assert not expected_unhunted_missing
