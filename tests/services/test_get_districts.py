import pytest
from cian_http.exceptions import ApiClientException

from external_offers.services.districts.exceptions import GetDistrictsByHouseError
from external_offers.services.districts.get_districts import get_districts_by_house_id


async def test_get_districts_by_house_id__api_exception_raised__rais_get_districts_error(
    mocker
):
    # arrange
    mocker.patch(
        'external_offers.services.districts.get_districts.v1_get_districts_by_child',
        side_effect=ApiClientException('Error')
    )

    # act and assert
    with pytest.raises(GetDistrictsByHouseError):
        await get_districts_by_house_id(
            house_id=mocker.sentinel.house_id
        )
