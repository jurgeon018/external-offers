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
    await postgresql.get_offers_in_progress_by_operator(operator_id)

    # assert
    pg.get().fetch.assert_called_with(query, operator_id)


async def test_set_waiting_offers_in_progress_by_client():
    # arrange
    query = """
        UPDATE
            offers_for_call
        SET
            status='inProgress'
        WHERE
            status = 'waiting'
            AND client_id = $1;
    """
    client_id = 1

    # act
    pg.get().fetch.return_value = future([])
    await postgresql.set_waiting_offers_in_progress_by_client(client_id)

    # assert
    pg.get().execute.assert_called_with(query, client_id)


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
    await postgresql.exists_offers_in_progress_by_operator(operator_id)

    # assert
    pg.get().fetchval.assert_called_with(query, operator_id)


async def test_set_offers_declined_by_client():
    # arrange
    query = 'UPDATE offers_for_call SET status=$2 WHERE offers_for_call.client_id = $1 AND offers_for_call.status = $3'
    client_id = 1
    pg.get().execute.return_value = future(None)

    # act
    await postgresql.set_offers_declined_by_client(client_id)

    # assert
    pg.get().execute.assert_called_with(query, client_id, 'declined', 'inProgress')


async def test_set_offers_set_call_missed_by_client():
    # arrange
    query = 'UPDATE offers_for_call SET status=$2 WHERE offers_for_call.client_id = $1 AND offers_for_call.status = $3'
    client_id = 1
    pg.get().execute.return_value = future(None)

    # act
    await postgresql.set_offers_call_missed_by_client(client_id)

    # assert
    pg.get().execute.assert_called_with(query, client_id, 'callMissed', 'inProgress')
