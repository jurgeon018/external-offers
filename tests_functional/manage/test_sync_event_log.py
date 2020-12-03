from unittest.mock import ANY

import pytest


async def test_sync_event_log__exist_draft_entry_in_interval__expected_message_to_kafka(
        pg,
        kafka_service,
        runner,
):
    # arrange
    operator_user_id = 7
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
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            3,
            'draft',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        """
        INSERT INTO public.event_log(
            id,
            offer_id,
            operator_user_id,
            status,
            created_at
        ) VALUES (
            '1',
            '1',
            7,
            'draft',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            cian_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 1, 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'accepted']
    )

    # act
    await runner.run_python_command('sync-event-log-with-kafka-analytics', '--date-from=11-10-2020', '--date-to=13-10-2020')

    # assert
    messages = await kafka_service.wait_messages(
        topic='preposition-admin.draft-announcements',
        count=1,
        timeout=4
    )
    assert len(messages) == 1

    assert messages[0].data == {
        'managerId': operator_user_id,
        'sourceUserId': '555bb598767308327e1dffbe7241486c',
        'date': ANY,
        'timestamp': ANY,
        'userId': 1,
        'phone': '+79812333292',
        'draft': 3
    }


async def test_sync_event_log__exist_in_progress_entry__expected_no_message_to_kafka(
        pg,
        kafka_service,
        runner,
):
    # arrange
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
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            3,
            'inProgress',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        """
        INSERT INTO public.event_log(
            id,
            offer_id,
            operator_user_id,
            status,
            created_at
        ) VALUES (
            '1',
            '1',
            7,
            'inProgress',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            cian_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 1, 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'inProgress']
    )

    # act
    await runner.run_python_command('sync-event-log-with-kafka-analytics')

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.draft-announcements',
            count=1,
            timeout=4
        )


async def test_sync_event_log__exist_draft_entry_in_wrong_interval__expected_no_message_to_kafka(
        pg,
        kafka_service,
        runner,
):
    # arrange
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
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            3,
            'draft',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        """
        INSERT INTO public.event_log(
            id,
            offer_id,
            operator_user_id,
            status,
            created_at
        ) VALUES (
            '1',
            '1',
            7,
            'draft',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            cian_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 1, 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'accepted']
    )

    # act
    await runner.run_python_command('sync-event-log-with-kafka-analytics', '--date-from=13-10-2020')

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.draft-announcements',
            count=1,
            timeout=4
        )

@pytest.mark.parametrize(
    (   
        'offer_status',
        'event_log_status',
        'client_status'
    ),(
        ('draft', 'draft', 'accepted'),
        ('declined', 'declined', 'declined'),
        ('callMissed', 'callMissed', 'callMissed')
    )
)
async def test_sync_event_log__exist_appliable_client_call_entry_in_interval__expected_message_to_kafka(
        pg,
        kafka_service,
        runner,
        offer_status,
        event_log_status,
        client_status
):
    # arrange
    operator_user_id = 7
    await pg.execute(
        f"""
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
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            3,
            '{offer_status}',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        f"""
        INSERT INTO public.event_log(
            id,
            offer_id,
            operator_user_id,
            status,
            created_at
        ) VALUES (
            '1',
            '1',
            7,
            '{event_log_status}',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        f"""
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            cian_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 1, 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, client_status]
    )

    # act
    await runner.run_python_command('sync-event-log-with-kafka-analytics', '--date-from=11-10-2020', '--date-to=13-10-2020')

    # assert
    messages = await kafka_service.wait_messages(
        topic='preposition-admin.calls',
        count=1,
        timeout=2.5
    )
    assert len(messages) == 1

    assert messages[0].data == {
        'managerId': operator_user_id,
        'sourceUserId': '555bb598767308327e1dffbe7241486c',
        'date': ANY,
        'timestamp': ANY,
        'userId': 1,
        'phone': '+79812333292',
        'status': client_status,
        'source': 'avito'
    }


async def test_sync_event_log__exist_in_progress_client_call_entry_in_interval__expected_no_message_to_kafka(
        pg,
        kafka_service,
        runner,
):
    # arrange
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
            'ddd86dec-20f5-4a70-bb3a-077b2754dfe6',
            '7',
            3,
            'draft',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        """
        INSERT INTO public.event_log(
            id,
            offer_id,
            operator_user_id,
            status,
            created_at
        ) VALUES (
            '1',
            '1',
            7,
            'draft',
            '2020-10-12 04:05:06'
            )
        """
    )
    await pg.execute(
        """
        INSERT INTO public.clients (
            client_id,
            avito_user_id,
            cian_user_id,
            client_name,
            client_phones,
            client_email,
            operator_user_id,
            status
        )
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        """,
        ['7', '555bb598767308327e1dffbe7241486c', 1, 'Иван Петров',
         ['+79812333292'], 'nemoy@gmail.com', 60024640, 'inProgress']
    )

    # act
    await runner.run_python_command('sync-event-log-with-kafka-analytics', '--date-from=11-10-2020', '--date-to=13-10-2020')

    # assert
    with pytest.raises(TimeoutError):
        await kafka_service.wait_messages(
            topic='preposition-admin.calls',
            count=1,
            timeout=4
        )
