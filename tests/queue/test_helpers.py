from external_offers.helpers.queue import _get_branch_suffix


async def test_get_branch_suffix(mocker):
    mocker.patch(
        'external_offers.helpers.queue.getenv',
        return_value='dev'
    )
    result = _get_branch_suffix()
    assert result == '.dev'
