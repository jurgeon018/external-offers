from cian_test_utils import future

from external_offers import pg
from external_offers.repositories import postgresql


async def test_get_client_in_progress_by_operator():
    # arrange
    query = ('SELECT clients.client_id, clients.avito_user_id, clients.cian_user_id, clients.client_name, clients'
             '.client_phones, clients.client_email, clients.status, clients.operator_user_id, clients.segment, cl'
             'ients.next_call, clients.calls_count, clients.last_call_id, clients.synced_with_grafana, clients.is'
             '_test, clients.main_account_chosen, clients.comment, clients.unactivated \nFROM clie'
             'nts \nWHERE clients.operator_user_id = $1 AND clients.status = $3 \n LIMIT $2')
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
    query = ('WITH first_suitable_offer_client_cte AS \n(SELECT clients.client_id AS client_id \n'
             'FROM clients JOIN offers_for_call ON offers_for_call.client_id = clients.client_id '
             '\nWHERE clients.unactivated IS false AND clients.operator_user_id IS NULL AND offers'
             '_for_call.status = $13 AND clients.status = $14 AND clients.is_test = false OR clien'
             'ts.unactivated IS false AND clients.operator_user_id = $7 AND offers_for_call.status'
             ' IN ($15, $16) AND clients.next_call <= $4 AND clients.is_test = false OR clients.un'
             'activated IS true AND clients.operator_user_id IS NULL AND offers_for_call.publicati'
             'on_status = $10 AND clients.is_test = false OR clients.unactivated IS true AND clien'
             'ts.operator_user_id = $8 AND offers_for_call.status IN ($17, $18) AND clients.next_c'
             'all <= $5 AND offers_for_call.publication_status = $11 AND clients.is_test = false O'
             'RDER BY offers_for_call.priority ASC NULLS LAST, offers_for_call.created_at DESC \n '
             'LIMIT $9 FOR UPDATE SKIP LOCKED)\n UPDATE clients SET status=$12, operator_user_id=$'
             '6, calls_count=(coalesce(clients.calls_count, $1) + $2), last_call_id=$3 FROM first_'
             'suitable_offer_client_cte WHERE clients.client_id = first_suitable_offer_client_cte.'
             'client_id RETURNING clients.client_id')
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
        mocker.ANY,
        default_one_more_call,
        default_one_more_call,
        default_one_more_call,
        default_one_more_call,
        'Draft',
        'Draft',
        'inProgress',
        'waiting',
        'waiting',
        'callLater',
        'callMissed',
        'callLater',
        'callMissed',
    )
