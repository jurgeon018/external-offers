from external_offers.services.offers_creator import create_phones_statuses


async def test_create_phones_statuses(mocker):
    # arrange
    mocker.patch(
        'external_offers.services.offers_creator.runtime_settings',
        new={
            'ENABLE_PHONES_STATUSES_CASHING': False,
        }
    )
    get_parsed_offers_for_account_prioritization_mock = mocker.patch(
        'external_offers.services.offers_creator.get_parsed_offers_for_account_prioritization',
    )

    # act
    await create_phones_statuses()

    # assert
    assert get_parsed_offers_for_account_prioritization_mock.assert_not_called
