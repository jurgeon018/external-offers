from typing import List

from cian_core.degradation import get_degradation_handler

from external_offers.entities import ClientAccountInfo
from external_offers.repositories.users import v2_get_users_by_phone
from external_offers.repositories.users.entities import V2GetUsersByPhone


async def get_client_accounts_by_phone_number(
    *,
    phone: str,
) -> List[ClientAccountInfo]:
    client_accounts = []
    response = await v2_get_users_by_phone(
        V2GetUsersByPhone(
            phone=phone
        )
    )
    user_profiles = response.users or []

    for profile in user_profiles:
        if not profile.state.is_active:
            continue

        source_user_type = profile.external_user_source_type
        if (
            source_user_type
            and (
                source_user_type.is_emls
                or source_user_type.is_sub_agents
                )
        ):
            continue

        client_accounts.append(
            ClientAccountInfo(
                cian_user_id=profile.cian_user_id,
                email=profile.email,
                is_agent=profile.is_agent
            )
        )

    return client_accounts


get_client_accounts_by_phone_number_degradation_handler = get_degradation_handler(
    func=get_client_accounts_by_phone_number,
    key='get_client_accounts_by_phone_number',
    default=[],
)
