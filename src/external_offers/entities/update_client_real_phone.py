from dataclasses import dataclass
from datetime import datetime


@dataclass
class UpdateClientRealPhoneRequest:
    client_id: str
    """Идентификатор клиента"""
    real_phone_number: str
    """Добытый телефон"""
    real_phone_number_hunted_at: datetime
    """Дата и время добычи телефона"""
