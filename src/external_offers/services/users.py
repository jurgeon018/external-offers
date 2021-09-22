import asyncio

from cian_http.exceptions import ApiClientException

from external_offers.repositories.users import v1_add_role_to_user, v1_get_realty_id
from external_offers.repositories.users.entities import AddRoleToUserRequest, V1GetRealtyId


async def check_cian_user_id(cian_user_id: int) -> bool:
    try:
        response = await v1_get_realty_id(
            V1GetRealtyId(cian_user_id=cian_user_id)
        )
        realty_id = response

    except ApiClientException:
        realty_id = None

    return bool(realty_id)


async def add_qa_role_to_user(cian_user_id: int) -> None:
    QA_ROLES = ['QA.HideUploadAnnouncements', 'Cian.QA']

    await asyncio.gather(
        *[
            v1_add_role_to_user(
                AddRoleToUserRequest(
                    user_id=cian_user_id,
                    role_name=role
                )
            ) for role in QA_ROLES
        ]
    )
