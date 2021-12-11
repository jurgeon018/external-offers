from external_offers.services.offers_creator import create_client_account_statuses


async def test_create_client_account_statuses(mocker):
    # arrange
    mocker.patch(
        'external_offers.services.offers_creator.runtime_settings',
        new={
            'ENABLE_client_account_statuses_CASHING': False,
        }
    )
    get_parsed_offers_for_account_prioritization_mock = mocker.patch(
        'external_offers.services.offers_creator.get_parsed_offers_for_account_prioritization',
    )

    # act
    await create_client_account_statuses()

    # assert
    assert get_parsed_offers_for_account_prioritization_mock.assert_not_called
