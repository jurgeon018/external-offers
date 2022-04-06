from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UpdateClientRealInfoRequest:
    client_id: str
    """Идентификатор клиента"""
    real_phone: Optional[str] = None
    """Добытый настоящий телефон"""
    real_name: Optional[str] = None
    """Добытое настоящее имя"""
    real_phone_hunted_at: Optional[datetime] = None
    """Дата и время добычи телефона"""
