from cian_test_utils import future

from external_offers import pg
from external_offers.repositories import postgresql


async def test_get_client_in_progress_by_operator():
    # arrange
    query = ('SELECT clients.client_id, clients.avito_user_id, clients.cian_user_id, clients.client_name, clients.'
             'client_phones, clients.client_email, clients.status, clients.operator_user_id, clients.segment, clie'
             'nts.next_call \nFROM clients \nWHERE clients.operator_user_id = $1 AND clients.status = $3 \n LIMIT $2')
    operator_id = 1

    # act
    pg.get().fetchrow.return_value = future(None)
    await postgresql.get_client_in_progress_by_operator(
        operator_id=operator_id
    )

    # assert
    pg.get().fetchrow.assert_called_with(query,  operator_id, operator_id, 'inProgress')


async def test_assign_suitable_client_to_operator(mocker):
    # arrange
    query = ('WITH first_suitable_offer_client_cte AS \n(SELECT clients.client_id AS client_id \nFROM clients JOIN'
             ' offers_for_call ON offers_for_call.client_id = clients.client_id \nWHERE clients.operator_user_id I'
             'S NULL AND offers_for_call.status = $6 AND clients.status = $7 OR clients.operator_user_id = $3 AND '
             'offers_for_call.status = $8 AND clients.next_call <= $1 ORDER BY offers_for_call.priority ASC NULLS '
             'LAST, offers_for_call.created_at ASC \n LIMIT $4 FOR UPDATE SKIP LOCKED)\n UPDATE clients SET status'
             '=$5, operator_user_id=$2 FROM first_suitable_offer_client_cte WHERE clients.client_id = first_suitab'
             'le_offer_client_cte.client_id RETURNING clients.client_id')
    operator_id = 1

    # act
    pg.get().fetchval.return_value = future(None)
    await postgresql.assign_suitable_client_to_operator(
        operator_id=operator_id
    )

    # assert
    pg.get().fetchval.assert_called_with(
        query,
        mocker.ANY,
        operator_id,
        operator_id,
        operator_id,
        'inProgress',
        'waiting',
        'waiting',
        'callLater'
    )
