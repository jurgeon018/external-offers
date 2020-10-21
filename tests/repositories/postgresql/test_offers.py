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
            status = 'inProgress'
            AND c.operator_user_id = $1
    """
    operator_id = 1

    # act
    pg.get().fetch.return_value = future([])
    await postgresql.get_offers_in_progress_by_operator(operator_id)

    # assert
    pg.get().fetch.assert_called_with(query, operator_id)
