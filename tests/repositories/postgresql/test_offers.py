from cian_test_utils import future

from external_offers import pg
from external_offers.repositories import postgresql


async def test_get_offers_in_progress_by_operator():
    # arrange
    query = """
        SELECT
            ofc.*
        FROM
            offers_for_call as ofc
        INNER JOIN
            clients as c
        ON
            ofc.client_id = c.client_id
        WHERE
            ofc.status = 'inProgress'
            AND c.operator_user_id = $1
    """
    operator_id = 1

    # act
    pg.get().fetch.return_value = future([])
    await postgresql.get_offers_in_progress_by_operator(
        operator_id=operator_id
    )

    # assert
    pg.get().fetch.assert_called_with(query, operator_id)


async def test_set_offers_in_progress_by_client():
    # arrange
    query = (
        'UPDATE offers_for_call SET status=$3, last_call_id=$2 '
        'WHERE offers_for_call.client_id = $1 RETURNING offers_for_call.id'
    )

    client_id = '1'
    call_id = 'test'
    pg.get().fetch.return_value = future([])

    # act
    await postgresql.set_offers_in_progress_by_client(
        client_id=client_id,
        call_id=call_id,
    )

    # assert
    pg.get().fetch.assert_called_with(
        query,
        client_id,
        call_id,
        'inProgress',
    )


async def test_exists_offers_in_progress_by_operator():
    # arrange
    query = """
        SELECT
            1
        FROM
            offers_for_call as ofc
        INNER JOIN
            clients as c
        ON
            ofc.client_id = c.client_id
        WHERE
            ofc.status = 'inProgress'
            AND c.operator_user_id = $1
        LIMIT 1
    """
    operator_id = 1
    pg.get().fetchval.return_value = future(False)

    # act
    pg.get().fetch.return_value = future([])
    await postgresql.exists_offers_in_progress_by_operator(
        operator_id=operator_id
    )

    # assert
    pg.get().fetchval.assert_called_with(query, operator_id)


async def test_set_offers_declined_by_client():
    # arrange
    query = (
        'UPDATE offers_for_call SET status=$2 '
        'WHERE offers_for_call.client_id = $1 AND offers_for_call.status = $3 '
        'RETURNING offers_for_call.id'
    )
    client_id = '1'
    pg.get().fetch.return_value = future([])

    # act
    await postgresql.set_offers_declined_by_client(
        client_id=client_id
    )

    # assert
    pg.get().fetch.assert_called_with(query, client_id, 'declined', 'inProgress')


async def test_set_offers_set_call_missed_by_client():
    # arrange
    query = (
        'UPDATE offers_for_call SET status=$3, priority=$2 WHERE offers_for_ca'
        'll.client_id = $1 AND offers_for_call.status = $4 RETURNING offers_for_call.id'
    )
    client_id = '1'
    priority = 200000
    pg.get().fetch.return_value = future([])

    # act
    await postgresql.set_offers_call_missed_by_client(
        client_id=client_id,
        team_settings={},
        team_id=None,
    )

    # assert
    pg.get().fetch.assert_called_with(query, client_id, priority, 'callMissed', 'inProgress')


async def test_get_enriched_offers_in_progress_by_operator():
    # arrange
    query = (
        '\n        SELECT\n            ofc.*,\n            po.source_object_model->>\'title\' as title,'
        '\n            po.source_object_model->>\'address\' as address\n        FROM\n            '
        'offers_for_call as ofc\n        INNER JOIN\n            clients as c\n        ON\n            '
        'ofc.client_id = c.client_id\n        INNER JOIN\n            parsed_offers as po\n        '
        'ON\n            ofc.parsed_id = po.id\n        WHERE\n            '
        'c.operator_user_id = $1\n            '
        'AND ofc.status = \'inProgress\'\n    '
    )
    operator_id = 123123
    pg.get().fetch.return_value = future([])
    # act
    await postgresql.get_enriched_offers_in_progress_by_operator(
        operator_id=operator_id,
    )
    # assert
    pg.get().fetch.assert_called_with(query, operator_id)
