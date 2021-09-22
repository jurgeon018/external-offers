from cian_http.exceptions import ApiClientException

from external_offers.repositories.users import v1_get_realty_id
from external_offers.repositories.users.entities import V1GetRealtyId


async def check_cian_user_id(cian_user_id: int) -> bool:
    try:
        response = await v1_get_realty_id(
            V1GetRealtyId(cian_user_id=cian_user_id)
        )
        realty_id = response

    except ApiClientException:
        realty_id = None

    return bool(realty_id)
