from dataclasses import dataclass
from typing import List
from external_offers.entities.create_test_offer import default_parsed_offer
# from cian_core.runtime_settings import runtime_settings

# default_client = runtime_settings.DEFAULT_TEST_CLIENT
default_client = {
    'avito_user_id': default_parsed_offer['source_user_id'],
    'segment':  default_parsed_offer['user_segment'],
    'client_phones': default_parsed_offer['source_object_model']['client_phones'],
    'client_name': default_parsed_offer['source_object_model']['contact'],
    'cian_user_id': '',
    'client_email': '',
    'main_account_chosen': False,
}

@dataclass
class CreateTestClientRequest:
    avito_user_id: str = default_client['avito_user_id']
    """Идентификатор пользователя на Авито"""
    client_phones: List[str] = default_client['client_phones']
    """Телефон клиента"""
    cian_user_id: str = default_client['cian_user_id']
    """Идентификатор пользователя на Циане"""
    client_name: str = default_client['client_name']
    """Имя клиента"""
    client_email: str = default_client['client_email']
    """Почтовый ящик клиента, к которому привязана учетная запись Циана"""
    segment: str = default_client['segment']
    """Сегмент пользователя"""
    main_account_chosen: bool = default_client['main_account_chosen']
    """Флаг выбора главного аккаунта(аккаунт выбранный при первом сохранении черновика)"""


@dataclass
class CreateTestClientResponse:
    success: bool
    """Статус операции"""
    message: str
    """Сообщение"""
