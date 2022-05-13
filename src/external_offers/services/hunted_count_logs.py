

from external_offers.repositories.postgresql.clients import get_hunted_numbers_by_operator_id
from external_offers.repositories.postgresql.hunted_count_logs import create_hunted_count_log_by_operator
from external_offers.repositories.postgresql.operators import get_operators


async def create_hunted_count_logs() -> None:
    operators = await get_operators()
    for operator in operators:
        operator_id = int(operator.operator_id)
        count = await get_hunted_numbers_by_operator_id(
            hunter_user_id=operator_id,
        )
        await create_hunted_count_log_by_operator(
            operator_user_id=operator_id,
            count=count,
        )
