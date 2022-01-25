from external_offers.entities import ClientDraftOffersCount, ClientWaitingOffersCount
from external_offers.services.offers_creator import prioritize_clients, prioritize_unactivated_clients


async def test_prioritize_clients_use_gather__raise_exception_in_prioritize_client(
    mocker,
    postgres,
):
    # arrange
    mocker.patch(
        'external_offers.services.offers_creator.get_client_by_client_id',
        side_effect=Exception(),
    )

    logger_mock = mocker.patch(
        'external_offers.services.offers_creator.logger.warning'
    )

    # act
    await prioritize_clients(
        waiting_clients_counts=[
            ClientWaitingOffersCount(
                client_id='705cf497-0f34-40e7-b6f2-b4a19e12af88',
                parsed_id='',
                waiting_offers_count=1,
            )
        ],
        team_settings={
            'maximum_active_offers_proportion': 1,
            'no_lk_smb_priority': 1,
            'no_active_smb_priority': 2,
            'keep_proportion_smb_priority': 3,
            'active_lk_homeowner_priority': 2,
            'no_lk_homeowner_priority': 4,
            'unactivated_client_priority': 1,
            'new_client_priority': 2,
            'call_missed_priority': 2,
            'call_later_priority': 1,
            'waiting_priority': 3,
            'smb_priority': 1,
            'homeowner_priority': 2,
            'main_regions_priority': {
                '2': 1, '4588': 2, '1': 3, '4593': 4, '4612': 5, '4897': 6, '4827': 7, '4557': 8, '5024': 9,
                '5048': 10, '4603': 11, '4914': 12, '4584': 13,
                '181462': 14, '184723': 15, '4606': 16, '4565': 17, '4567': 18, '4574': 19, '4580': 20, '4597': 21,
                '4560': 34, '4618': 28, '4608': 24, '4615': 25, '4743': 26, '4596': 27, '4568': 29, '4605': 30,
                '4619': 31, '4614': 32, '4625': 33, '4621': 35, '4636': 36, '4576': 37, '4601': 38, '4607': 39,
                '4561': 40, '4609': 41, '4564': 42, '4570': 43, '4594': 44, '4613': 45, '4591': 46, '4581': 47,
                '4566': 48, '4575': 49, '4589': 50, '4553': 51, '4617': 52, '4579': 53, '4582': 54, '4624': 55,
                '4586': 56, '4635': 57, '4562': 58, '4602': 59, '4633': 60, '4629': 61, '4558': 62, '4571': 63,
                '4587': 64, '4600': 65, '4585': 66, '4592': 67, '4583': 68, '4631': 69
            },
            'sale_priority': 1,
            'rent_priority': 2,
            'flat_priority': 1,
            'suburban_priority': 2,
            'commercial_priority': 3,
            'regions': [4580], 'segments': ['d'],
            'categories': ['flatSale', 'flatRent', 'officeRent', 'houseRent', 'officeSale', 'houseSale'],
        },
        client_account_statuses={},
    )
    # assert
    assert logger_mock.called is True


async def test_prioritize_unactivated_clients_use_gather__raise_exception_in_prioritize_client(
    mocker,
    postgres,
):
    # arrange
    mocker.patch(
        'external_offers.services.offers_creator.get_client_by_client_id',
        side_effect=Exception(),
    )

    logger_mock = mocker.patch(
        'external_offers.services.offers_creator.logger.warning'
    )

    # act
    await prioritize_unactivated_clients(
        clients_priority={},
        unactivated_clients_counts=[
            ClientDraftOffersCount(
                client_id='1',
                draft_offers_count=1,
                priority=223456789,
                team_priorities=None,
            ),
        ],
        team_settings={
            'maximum_active_offers_proportion': 1,
            'no_lk_smb_priority': 1,
            'no_active_smb_priority': 2,
            'keep_proportion_smb_priority': 3,
            'active_lk_homeowner_priority': 2,
            'no_lk_homeowner_priority': 4,
            'unactivated_client_priority': 1,
            'new_client_priority': 2,
            'call_missed_priority': 2,
            'call_later_priority': 1,
            'waiting_priority': 3,
            'smb_priority': 1,
            'homeowner_priority': 2,
            'main_regions_priority': {
                '2': 1, '4588': 2, '1': 3, '4593': 4, '4612': 5, '4897': 6, '4827': 7, '4557': 8, '5024': 9,
                '5048': 10, '4603': 11, '4914': 12, '4584': 13,
                '181462': 14, '184723': 15, '4606': 16, '4565': 17, '4567': 18, '4574': 19, '4580': 20, '4597': 21,
                '4560': 34, '4618': 28, '4608': 24, '4615': 25, '4743': 26, '4596': 27, '4568': 29, '4605': 30,
                '4619': 31, '4614': 32, '4625': 33, '4621': 35, '4636': 36, '4576': 37, '4601': 38, '4607': 39,
                '4561': 40, '4609': 41, '4564': 42, '4570': 43, '4594': 44, '4613': 45, '4591': 46, '4581': 47,
                '4566': 48, '4575': 49, '4589': 50, '4553': 51, '4617': 52, '4579': 53, '4582': 54, '4624': 55,
                '4586': 56, '4635': 57, '4562': 58, '4602': 59, '4633': 60, '4629': 61, '4558': 62, '4571': 63,
                '4587': 64, '4600': 65, '4585': 66, '4592': 67, '4583': 68, '4631': 69
            },
            'sale_priority': 1,
            'rent_priority': 2,
            'flat_priority': 1,
            'suburban_priority': 2,
            'commercial_priority': 3,
            'regions': [4580], 'segments': ['d'],
            'categories': ['flatSale', 'flatRent', 'officeRent', 'houseRent', 'officeSale', 'houseSale'],
        },
    )
    # assert
    assert logger_mock.called is True
