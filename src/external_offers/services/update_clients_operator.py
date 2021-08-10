from external_offers.entities.update_clients_operator import UpdateClientsOperatorRequest, UpdateClientsOperatorResponse
from external_offers.repositories.postgresql.clients import update_clients_operator

async def update_clients_operator_public(
    request: UpdateClientsOperatorRequest, user_id: int
) -> UpdateClientsOperatorResponse:
    old_operator_id = request.old_operator_id
    new_operator_id = request.new_operator_id
    await update_clients_operator(
        old_operator_id=old_operator_id,
        new_operator_id=new_operator_id,
    )
    return UpdateClientsOperatorResponse(
        success=True,
        message=f'Задания оператора "{old_operator_id}", были переданы оператору "{new_operator_id}".'
    )
