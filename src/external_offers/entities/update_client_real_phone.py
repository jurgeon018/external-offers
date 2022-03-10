from dataclasses import dataclass


@dataclass
class UpdateClientRealPhoneRequest:
    client_id: str
    """Идентификатор клиента"""
    real_phone_number: str
    """Телефон"""
