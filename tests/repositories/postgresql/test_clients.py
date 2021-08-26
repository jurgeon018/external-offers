from cian_test_utils import future

from external_offers import pg
from external_offers.repositories import postgresql


async def test_get_client_in_progress_by_operator():
    # arrange
    query = ('SELECT clients.client_id, clients.avito_user_id, clients.cian_user_id, clients.client_name, clients'
             '.client_phones, clients.client_email, clients.status, clients.operator_user_id, clients.segment, cl'
             'ients.next_call, clients.calls_count, clients.last_call_id, clients.synced_with_grafana, clients.main_account_chosen, clients.comment \nFROM clie'
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
    query = (
        'WITH first_suitable_offer_client_cte AS \n(SELECT clients.client_id AS client_id \n'
        'FROM clients JOIN offers_for_call ON offers_for_call.client_id = clients.client_id \n'
        'WHERE clients.operator_user_id IS NULL AND offers_for_call.status = $32 AND clients.status = $33'
        ' AND coalesce(offers_for_call.category, $19) NOT IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5,'
        ' $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) OR clients.operator_user_id = $29 AND'
        ' offers_for_call.status IN ($34, $35) AND clients.next_call <= $27 AND coalesce(offers_for_call.category, $19)'
        ' NOT IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18)'
        ' ORDER BY offers_for_call.priority ASC NULLS LAST, offers_for_call.created_at DESC \n'
        ' LIMIT $30 FOR UPDATE SKIP LOCKED)\n UPDATE clients SET status=$31, operator_user_id=$28, '
        'calls_count=(coalesce(clients.calls_count, $1) + $12), last_call_id=$26 FROM first_suitable_offer_client_cte '
        'WHERE clients.client_id = first_suitable_offer_client_cte.client_id RETURNING clients.client_id'
    )

    operator_id = 1
    default_no_calls = 0
    default_one_more_call = 1
    expected_call_id = '1'
    default_offer_category = ''

    # act
    pg.get().fetchval.return_value = future(None)
    await postgresql.assign_suitable_client_to_operator(
        operator_id=operator_id,
        call_id='1',
        operator_roles=[]
    )

    # assert
    pg.get().fetchval.assert_called_with(
        query,
        default_no_calls,
        'businessSale',
        'commercialLandSale',
        'publicCateringSale',
        'carServiceSale',
        'domesticServicesSale',
        'officeRent',
        'warehouseRent',
        'shoppingAreaRent',
        'industryRent',
        'buildingRent',
        default_one_more_call,
        'freeAppointmentObjectRent',
        'businessRent',
        'commercialLandRent',
        'publicCateringRent',
        'carServiceRent',
        'domesticServicesRent',
        default_offer_category,
        'officeSale',
        'warehouseSale',
        'shoppingAreaSale',
        'industrySale',
        'buildingSale',
        'freeAppointmentObjectSale',
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


async def test_assign_suitable_client_to_operator__commercial_operator(mocker):
    # arrange
    query = (
        'WITH first_suitable_offer_client_cte AS \n(SELECT clients.client_id AS client_id \n'
        'FROM clients JOIN offers_for_call ON offers_for_call.client_id = clients.client_id \n'
        'WHERE clients.operator_user_id IS NULL AND offers_for_call.status = $32 AND clients.status = $33'
        ' AND coalesce(offers_for_call.category, $19) IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5,'
        ' $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) OR clients.operator_user_id = $29 AND'
        ' offers_for_call.status IN ($34, $35) AND clients.next_call <= $27 AND coalesce(offers_for_call.category, $19)'
        ' IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18)'
        ' ORDER BY offers_for_call.priority ASC NULLS LAST, offers_for_call.created_at DESC \n'
        ' LIMIT $30 FOR UPDATE SKIP LOCKED)\n UPDATE clients SET status=$31, operator_user_id=$28, '
        'calls_count=(coalesce(clients.calls_count, $1) + $12), last_call_id=$26 FROM first_suitable_offer_client_cte '
        'WHERE clients.client_id = first_suitable_offer_client_cte.client_id RETURNING clients.client_id'
    )

    operator_id = 1
    default_no_calls = 0
    default_one_more_call = 1
    expected_call_id = '1'
    default_offer_category = ''

    # act
    pg.get().fetchval.return_value = future(None)
    await postgresql.assign_suitable_client_to_operator(
        operator_id=operator_id,
        call_id='1',
        operator_roles=['CommercialPrepublicationModerator']
    )

    # assert
    pg.get().fetchval.assert_called_with(
        query,
        default_no_calls,
        'businessSale',
        'commercialLandSale',
        'publicCateringSale',
        'carServiceSale',
        'domesticServicesSale',
        'officeRent',
        'warehouseRent',
        'shoppingAreaRent',
        'industryRent',
        'buildingRent',
        default_one_more_call,
        'freeAppointmentObjectRent',
        'businessRent',
        'commercialLandRent',
        'publicCateringRent',
        'carServiceRent',
        'domesticServicesRent',
        default_offer_category,
        'officeSale',
        'warehouseSale',
        'shoppingAreaSale',
        'industrySale',
        'buildingSale',
        'freeAppointmentObjectSale',
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
