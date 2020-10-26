from cian_test_utils import future

from external_offers import pg
from external_offers.repositories import postgresql


async def test_get_client_by_operator():
    # arrange
    query = """
        SELECT
            *
        FROM
            clients as c
        WHERE
            c.operator_user_id = $1
        LIMIT 1
    """
    operator_id = 1

    # act
    pg.get().fetchrow.return_value = future(None)
    await postgresql.get_client_by_operator(operator_id)

    # assert
    pg.get().fetchrow.assert_called_with(query, operator_id)


async def test_assign_waiting_client_to_operator():
    # arrange
    query = """
        WITH cte1 as (
            SELECT
                c.client_id as client_id
            FROM
                clients as c
            INNER JOIN
                offers_for_call as ofc
            ON
                ofc.client_id = c.client_id
            WHERE
                c.operator_user_id IS NULL
                AND ofc.status = 'waiting'
            ORDER BY
                ofc.created_at
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )


        UPDATE
            clients
        SET
            operator_user_id = $1
        FROM
            cte1
        WHERE
            clients.client_id = cte1.client_id
        RETURNING
            clients.client_id
    """
    operator_id = 1

    # act
    pg.get().fetchval.return_value = future(None)
    await postgresql.assign_waiting_client_to_operator(operator_id)

    # assert
    pg.get().fetchval.assert_called_with(query, operator_id)
