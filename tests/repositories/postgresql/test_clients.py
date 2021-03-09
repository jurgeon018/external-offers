from cian_test_utils import future

from external_offers import pg
from external_offers.repositories import postgresql


async def test_get_client_in_progress_by_operator():
    # arrange
    query = ('SELECT clients.client_id, clients.avito_user_id, clients.cian_user_id, clients.client_name, clients.cli'
             'ent_phones, clients.client_email, clients.status, clients.operator_user_id, clients.segment, clients.ne'
             'xt_call, clients.calls_count, clients.last_call_id \nFROM clients \nWHERE clients.operator_user_id = $1'
             ' AND clients.status = $3 \n LIMIT $2')
    operator_id = 1

    # act
    pg.get().fetchrow.return_value = future(None)
    await postgresql.get_client_in_progress_by_operator(
        operator_id=operator_id
    )

    # assert
    pg.get().fetchrow.assert_called_with(query, operator_id, operator_id, 'inProgress')


async def test_assign_suitable_client_to_operator(mocker):
    # arrange
    query = ('WITH first_suitable_offer_client_cte AS \n(SELECT clients.client_id AS client_id \nFROM clients JOIN o'
             'ffers_for_call ON offers_for_call.client_id = clients.client_id \nWHERE clients.operator_user_id IS NU'
             'LL AND offers_for_call.status = $9 AND clients.status = $10 OR clients.operator_user_id = $6 AND offer'
             's_for_call.status IN ($11, $12) AND clients.next_call <= $4 ORDER BY offers_for_call.priority ASC NULL'
             'S LAST, offers_for_call.created_at ASC \n LIMIT $7 FOR UPDATE SKIP LOCKED)\n UPDATE clients SET status'
             '=$8, operator_user_id=$5, calls_count=(coalesce(clients.calls_count, $1) + $2), last_call_id=$3 FROM f'
             'irst_suitable_offer_client_cte WHERE clients.client_id = first_suitable_offer_client_cte.client_id RET'
             'URNING clients.client_id')
    operator_id = 1
    default_no_calls = 0
    default_one_more_call = 1
    expected_call_id = '1'

    # act
    pg.get().fetchval.return_value = future(None)
    await postgresql.assign_suitable_client_to_operator(
        operator_id=operator_id,
        call_id='1'
    )

    # assert
    pg.get().fetchval.assert_called_with(
        query,
        default_no_calls,
        default_one_more_call,
        expected_call_id,
        mocker.ANY,
        operator_id,
        operator_id,
        operator_id,
        'inProgress',
        'waiting',
        'waiting',
        'callLater',
        'callMissed'
    )
