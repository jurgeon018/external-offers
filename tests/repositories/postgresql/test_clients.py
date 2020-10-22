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
