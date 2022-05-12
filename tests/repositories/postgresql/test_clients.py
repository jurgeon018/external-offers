import pytest
from cian_test_utils import future

from external_offers import pg
from external_offers.entities.teams import TeamInfo
from external_offers.enums.teams import TeamType
from external_offers.repositories import postgresql


async def test_get_client_in_progress_by_operator():
    # arrange
    query = (
        'SELECT clients.client_id, clients.avito_user_id, clients.cian_user_id, clients.client_name, '
        'clients.client_phones, clients.real_phone, clients.real_name, clients.real_phone_hunted_at, '
        'clients.client_email, clients.status, clients.operator_user_id, clients.hunter_user_id, clients.segment, '
        'clients.subsegment, clients.next_call, clients.calls_count, clients.last_call_id, '
        'clients.synced_with_grafana, clients.is_test, clients.main_account_chosen, clients.comment, '
        'clients.team_id, clients.reason_of_decline, clients.additional_numbers, clients.additional_emails, '
        'clients.unactivated, clients.drafted_at, clients.published_at \nFROM clients \nWHERE '
        'clients.operator_user_id = $1 AND clients.status = $3 \n LIMIT $2'
    )
    operator_id = 1

    # act
    pg.get().fetchrow.return_value = future(None)
    await postgresql.get_client_in_progress_by_operator(
        operator_id=operator_id
    )

    # assert
    pg.get().fetchrow.assert_called_with(query, operator_id, operator_id, 'inProgress')


@pytest.mark.skip(reason='')
async def test_assign_suitable_client_to_operator(
    mocker,
    fake_settings,
):
    # arrange
    await fake_settings.set(
        ENABLE_TEAM_TYPES=False
    )
    operator_id = 1
    default_no_calls = 0
    default_one_more_call = 1
    expected_call_id = '1'
    default_offer_category = ''
    # https://www.joydeepdeb.com/tools/line-break.html
    mocker.patch(
        'external_offers.repositories.postgresql.clients.get_operator_by_id',
        return_value=future(None),
    )
    query = (
        'WITH first_suitable_offer_client_cte AS \n(SELECT clients.client_id AS client_id \nFROM clients JOIN offers_for_call ON offers_for_call.client_id = clients.client_id \nWHERE clients.unactivated IS false AND offers_for_call.publication_status IS NULL AND (clients.operator_user_id IS NOT $31 OR clients.operator_user_id IS NULL) AND offers_for_call.status = $40 AND clients.status = $41 AND clients.is_test = false AND coalesce(offers_for_call.category, $19) NOT IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) AND offers_for_call.priority != $36 OR clients.unactivated IS false AND offers_for_call.publication_status IS NULL AND clients.operator_user_id = $32 AND offers_for_call.status IN ($42, $43) AND clients.next_call <= $27 AND clients.is_test = false AND coalesce(offers_for_call.category, $19) NOT IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) AND offers_for_call.priority != $36 OR clients.unactivated IS true AND clients.operator_user_id = $33 AND clients.next_call <= $28 AND offers_for_call.publication_status = $37 AND clients.status NOT IN ($44) AND clients.is_test = false AND coalesce(offers_for_call.category, $19) NOT IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) AND offers_for_call.priority != $36 OR clients.unactivated IS true AND clients.operator_user_id = $34 AND offers_for_call.status IN ($45, $46) AND clients.next_call <= $29 AND offers_for_call.publication_status = $38 AND clients.is_test = false AND coalesce(offers_for_call.category, $19) NOT IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) AND offers_for_call.priority != $36 ORDER BY offers_for_call.priority ASC NULLS LAST, offers_for_call.created_at DESC \n LIMIT $35 FOR UPDATE SKIP LOCKED)\n UPDATE clients SET status=$39, operator_user_id=$30, calls_count=(coalesce(clients.calls_count, $1) + $12), last_call_id=$26, team_id=$47 FROM first_suitable_offer_client_cte WHERE clients.client_id = first_suitable_offer_client_cte.client_id RETURNING clients.client_id'
    )
    args = (
        0, 'businessSale', 'commercialLandSale', 'publicCateringSale', 'carServiceSale', 'domesticServicesSale', 'officeRent', 'warehouseRent', 'shoppingAreaRent', 'industryRent', 'buildingRent', 1, 'freeAppointmentObjectRent', 'businessRent', 'commercialLandRent', 'publicCateringRent', 'carServiceRent', 'domesticServicesRent', '', 'officeSale', 'warehouseSale', 'shoppingAreaSale', 'industrySale', 'buildingSale', 'freeAppointmentObjectSale', '1', mocker.ANY, mocker.ANY, mocker.ANY, 1, 1, 1, 1, 1, 1, -1, 'Draft', 'Draft', 'inProgress', 'waiting', 'waiting', 'callLater', 'callMissed', 'declined', 'callLater', 'callMissed', None
    )
    # act
    pg.get().fetchval.return_value = future(None)
    await postgresql.assign_suitable_client_to_operator(
        operator_id=operator_id,
        call_id='1',
        operator_roles=[]
    )

    # assert
    pg.get().fetchval.assert_called_with(query, *args)


@pytest.mark.skip(reason='')
async def test_assign_suitable_client_to_operator__commercial_operator(
    mocker,
    fake_settings,
):
    # arrange
    await fake_settings.set(
        ENABLE_TEAM_TYPES=False
    )
    operator_id = 1
    default_no_calls = 0
    default_one_more_call = 1
    expected_call_id = '1'
    default_offer_category = ''
    # https://www.joydeepdeb.com/tools/line-break.html
    mocker.patch(
        'external_offers.repositories.postgresql.clients.get_operator_by_id',
        return_value=future(None),
    )
    query = (
        'WITH first_suitable_offer_client_cte AS \n(SELECT clients.client_id AS client_id \nFROM clients JOIN offers_for_call ON offers_for_call.client_id = clients.client_id \nWHERE clients.unactivated IS false AND offers_for_call.publication_status IS NULL AND (clients.operator_user_id IS NOT $31 OR clients.operator_user_id IS NULL) AND offers_for_call.status = $40 AND clients.status = $41 AND clients.is_test = false AND coalesce(offers_for_call.category, $19) IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) AND offers_for_call.priority != $36 OR clients.unactivated IS false AND offers_for_call.publication_status IS NULL AND clients.operator_user_id = $32 AND offers_for_call.status IN ($42, $43) AND clients.next_call <= $27 AND clients.is_test = false AND coalesce(offers_for_call.category, $19) IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) AND offers_for_call.priority != $36 OR clients.unactivated IS true AND clients.operator_user_id = $33 AND clients.next_call <= $28 AND offers_for_call.publication_status = $37 AND clients.status NOT IN ($44) AND clients.is_test = false AND coalesce(offers_for_call.category, $19) IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) AND offers_for_call.priority != $36 OR clients.unactivated IS true AND clients.operator_user_id = $34 AND offers_for_call.status IN ($45, $46) AND clients.next_call <= $29 AND offers_for_call.publication_status = $38 AND clients.is_test = false AND coalesce(offers_for_call.category, $19) IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) AND offers_for_call.priority != $36 ORDER BY offers_for_call.priority ASC NULLS LAST, offers_for_call.created_at DESC \n LIMIT $35 FOR UPDATE SKIP LOCKED)\n UPDATE clients SET status=$39, operator_user_id=$30, calls_count=(coalesce(clients.calls_count, $1) + $12), last_call_id=$26, team_id=$47 FROM first_suitable_offer_client_cte WHERE clients.client_id = first_suitable_offer_client_cte.client_id RETURNING clients.client_id'
    )
    args = (
        0, 'businessSale', 'commercialLandSale', 'publicCateringSale', 'carServiceSale', 'domesticServicesSale', 'officeRent', 'warehouseRent', 'shoppingAreaRent', 'industryRent', 'buildingRent', 1, 'freeAppointmentObjectRent', 'businessRent', 'commercialLandRent', 'publicCateringRent', 'carServiceRent', 'domesticServicesRent', '', 'officeSale', 'warehouseSale', 'shoppingAreaSale', 'industrySale', 'buildingSale', 'freeAppointmentObjectSale', '1', mocker.ANY, mocker.ANY, mocker.ANY, 1, 1, 1, 1, 1, 1, -1, 'Draft', 'Draft', 'inProgress', 'waiting', 'waiting', 'callLater', 'callMissed', 'declined', 'callLater', 'callMissed', None
    )

    # act
    pg.get().fetchval.return_value = future(None)
    await postgresql.assign_suitable_client_to_operator(
        operator_id=operator_id,
        call_id='1',
        operator_roles=['CommercialPrepublicationModerator']
    )

    # assert
    pg.get().fetchval.assert_called_with(query, *args)


async def test_assign_suitable_client_to_operator__only_hunted_ct_attractor_teams(
    mocker,
    fake_settings,
):
    # arrange
    team_id = 58
    await fake_settings.set(
        ENABLE_TEAM_TYPES=True,
        ONLY_HUNTED_CT_ATTRACTOR_TEAM_ID=[team_id]
    )
    operator_id = 1
    # https://www.joydeepdeb.com/tools/line-break.html
    mocker.patch(
        'external_offers.repositories.postgresql.clients.get_operator_by_id',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.repositories.postgresql.clients.get_team_info',
        return_value=TeamInfo(
            team_id=str(team_id),
            team_settings={
                'return_to_queue_days_after_hunted': 2,
            },
            team_type=TeamType.attractor,
        ),
    )
    query = (
        'WITH first_suitable_offer_client_cte AS \n(SELECT clients.client_id AS client_id \nFRO'
        'M clients JOIN (offers_for_call JOIN parsed_offers ON offers_for_call.parsed_id = pars'
        'ed_offers.id) ON offers_for_call.client_id = clients.client_id \nWHERE clients.unactiv'
        'ated IS false AND offers_for_call.publication_status IS NULL AND (clients.operator_use'
        'r_id != $31 AND clients.real_phone_hunted_at IS NOT NULL OR clients.operator_user_id '
        'IS NULL AND clients.real_phone_hunted_at IS NULL) AND offers_for_call.status = $40 AN'
        'D clients.status = $41 AND clients.is_test = false AND coalesce(offers_for_call.categor'
        'y, $19) IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $1'
        '3, $14, $15, $16, $17, $18) AND parsed_offers.is_calltracking IS true AND clients.rea'
        'l_phone_hunted_at IS NOT NULL AND clients.real_phone_hunted_at <= $38 OR clients.unac'
        'tivated IS false AND offers_for_call.publication_status IS NULL AND clients.operator_'
        'user_id = $32 AND offers_for_call.status IN ($42, $43) AND clients.next_call <= $27 AN'
        'D clients.is_test = false AND coalesce(offers_for_call.category, $19) IN ($20, $21, $2'
        '2, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $'
        '18) OR clients.unactivated IS true AND clients.operator_user_id = $33 AND clients.next'
        '_call <= $28 AND offers_for_call.publication_status = $36 AND clients.status NOT IN ($4'
        '4) AND clients.is_test = false AND coalesce(offers_for_call.category, $19) IN ($20, $2'
        '1, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $1'
        '7, $18) OR clients.unactivated IS true AND clients.operator_user_id = $34 AND offers_fo'
        'r_call.status IN ($45, $46) AND clients.next_call <= $29 AND offers_for_call.publicatio'
        'n_status = $37 AND clients.is_test = false AND coalesce(offers_for_call.category, $19) I'
        'N ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $1'
        '5, $16, $17, $18) ORDER BY offers_for_call.priority ASC NULLS LAST, offers_for_call.crea'
        'ted_at DESC \n LIMIT $35 FOR UPDATE SKIP LOCKED)\n UPDATE clients SET status=$39, operat'
        'or_user_id=$30, calls_count=(coalesce(clients.calls_count, $1) + $12), last_call_id=$2'
        '6, team_id=$47 FROM first_suitable_offer_client_cte WHERE clients.client_id = first_su'
        'itable_offer_client_cte.client_id RETURNING clients.client_id'
    )
    args = (
        0,
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
        1,
        'freeAppointmentObjectRent',
        'businessRent',
        'commercialLandRent',
        'publicCateringRent',
        'carServiceRent',
        'domesticServicesRent',
        '',
        'officeSale',
        'warehouseSale',
        'shoppingAreaSale',
        'industrySale',
        'buildingSale',
        'freeAppointmentObjectSale',
        '1',
        mocker.ANY,
        mocker.ANY,
        mocker.ANY,
        1,
        1,
        1,
        1,
        1,
        1,
        'Draft',
        'Draft',
        mocker.ANY,
        'inProgress',
        'waiting',
        'waiting',
        'callLater',
        'callMissed',
        'declined',
        'callLater',
        'callMissed',
        '58'
    )

    # act
    pg.get().fetchval.return_value = future(None)
    await postgresql.assign_suitable_client_to_operator(
        operator_id=operator_id,
        call_id='1',
        operator_roles=['CommercialPrepublicationModerator']
    )

    # assert
    pg.get().fetchval.assert_called_with(query, *args)


async def test_assign_suitable_client_to_operator__only_unhunted_ct_attractor_teams(
    mocker,
    fake_settings,
):
    # arrange
    team_id = 58
    await fake_settings.set(
        ENABLE_TEAM_TYPES=True,
        # ONLY_UNHUNTED_CT_ATTRACTOR_TEAM_ID=[team_id]
    )
    operator_id = 1
    # https://www.joydeepdeb.com/tools/line-break.html
    mocker.patch(
        'external_offers.repositories.postgresql.clients.get_operator_by_id',
        return_value=future(None),
    )
    mocker.patch(
        'external_offers.repositories.postgresql.clients.get_team_info',
        return_value=TeamInfo(
            team_id=str(team_id),
            team_settings={
                'return_to_queue_days_after_hunted': 2,
                'enable_only_unhunted_ct': True,
            },
            team_type=TeamType.attractor,
        ),
    )
    query = (
        'WITH first_suitable_offer_client_cte AS \n(SELECT clients.client_id AS client_id \nFROM '
        'clients JOIN (offers_for_call JOIN parsed_offers ON offers_for_call.parsed_id = '
        'parsed_offers.id) ON offers_for_call.client_id = clients.client_id \nWHERE '
        'clients.unactivated IS false AND offers_for_call.publication_status IS NULL AND '
        '(clients.operator_user_id != $31 AND clients.real_phone_hunted_at IS NOT NULL OR '
        'clients.operator_user_id IS NULL AND clients.real_phone_hunted_at IS NULL) AND '
        'offers_for_call.status = $39 AND clients.status = $40 AND clients.is_test = false '
        'AND coalesce(offers_for_call.category, $19) IN ($20, $21, $22, $23, $24, $25, $2, $3, '
        '$4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) AND '
        'parsed_offers.is_calltracking IS true AND clients.real_phone_hunted_at IS NULL OR '
        'clients.unactivated IS false AND offers_for_call.publication_status IS NULL AND '
        'clients.operator_user_id = $32 AND offers_for_call.status IN ($41, $42) AND '
        'clients.next_call <= $27 AND clients.is_test = false AND coalesce(offers_for_call.category, '
        '$19) IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, '
        '$15, $16, $17, $18) OR clients.unactivated IS true AND clients.operator_user_id = $33 AND '
        'clients.next_call <= $28 AND offers_for_call.publication_status = $36 AND clients.status NOT '
        'IN ($43) AND clients.is_test = false AND coalesce(offers_for_call.category, $19) IN ($20, '
        '$21, $22, $23, $24, $25, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, '
        '$18) OR clients.unactivated IS true AND clients.operator_user_id = $34 AND '
        'offers_for_call.status IN ($44, $45) AND clients.next_call <= $29 AND '
        'offers_for_call.publication_status = $37 AND clients.is_test = false AND '
        'coalesce(offers_for_call.category, $19) IN ($20, $21, $22, $23, $24, $25, $2, $3, $4, '
        '$5, $6, $7, $8, $9, $10, $11, $13, $14, $15, $16, $17, $18) ORDER BY '
        'offers_for_call.priority ASC NULLS LAST, offers_for_call.created_at DESC \n LIMIT '
        '$35 FOR UPDATE SKIP LOCKED)\n UPDATE clients SET status=$38, operator_user_id=$30, '
        'calls_count=(coalesce(clients.calls_count, $1) + $12), last_call_id=$26, team_id=$46 '
        'FROM first_suitable_offer_client_cte WHERE clients.client_id = '
        'first_suitable_offer_client_cte.client_id RETURNING clients.client_id'
    )
    args = (
        0, 'businessSale',
        'commercialLandSale',
        'publicCateringSale',
        'carServiceSale',
        'domesticServicesSale',
        'officeRent',
        'warehouseRent',
        'shoppingAreaRent',
        'industryRent',
        'buildingRent', 1, 'freeAppointmentObjectRent',
        'businessRent',
        'commercialLandRent',
        'publicCateringRent',
        'carServiceRent',
        'domesticServicesRent',
        '',
        'officeSale',
        'warehouseSale',
        'shoppingAreaSale',
        'industrySale',
        'buildingSale',
        'freeAppointmentObjectSale',
        '1',
        mocker.ANY,
        mocker.ANY,
        mocker.ANY,
        1,
        1,
        1,
        1,
        1,
        1,
        'Draft',
        'Draft',
        'inProgress',
        'waiting',
        'waiting',
        'callLater',
        'callMissed',
        'declined',
        'callLater',
        'callMissed',
        '58'
    )

    # act
    pg.get().fetchval.return_value = future(None)
    await postgresql.assign_suitable_client_to_operator(
        operator_id=operator_id,
        call_id='1',
        operator_roles=['CommercialPrepublicationModerator']
    )

    # assert
    pg.get().fetchval.assert_called_with(query, *args)
