from cian_core.runtime_settings import runtime_settings
from external_offers.entities.create_test_client import CreateTestClientRequest, CreateTestClientResponse
from external_offers.entities.clients import Client, UserSegment

from external_offers.repositories.postgresql.clients import save_client

from external_offers.enums.client_status import ClientStatus

from external_offers.helpers.uuid import generate_guid


def get_attr(obj, attr):
    if isinstance(obj, CreateTestClientRequest):
        return getattr(obj, attr)
    elif isinstance(obj, dict):
        return obj[attr]


async def create_test_client_public(request: CreateTestClientRequest, user_id: int) -> CreateTestClientResponse:
    client_id = generate_guid()
    if request.use_default:
        obj = runtime_settings.DEFAULT_TEST_CLIENT
    else:
        obj = request
    avito_user_id = get_attr(obj, 'avito_user_id')
    client_phones = get_attr(obj, 'client_phone')
    client_name = get_attr(obj, 'client_name')
    cian_user_id = get_attr(obj, 'cian_user_id')
    client_email = get_attr(obj, 'client_email')
    segment = get_attr(obj, 'segment')
    main_account_chosen = get_attr(obj, 'main_account_chosen')
    client = Client(
        # dynamic params from request
        avito_user_id = avito_user_id,
        client_phones = [client_phones],
        client_name = client_name,
        cian_user_id = cian_user_id,
        client_email = client_email,
        segment = UserSegment.from_str(segment),
        main_account_chosen = main_account_chosen,
        # static params
        is_test = True,
        client_id = client_id,
        status = ClientStatus.waiting,
        operator_user_id = None,
        last_call_id = None,
        calls_count = 0,
        next_call = None,
    )
    await save_client(
        client=client
    )
    return CreateTestClientResponse(
        success=True,
        message=f'Тестовый клиент был успешно создан.',
        client_id=client_id,
    )
