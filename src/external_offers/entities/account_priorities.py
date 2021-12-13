from dataclasses import dataclass
from datetime import datetime


@dataclass
class AccountPriority:
    priority_id: int
    """ID приоритета в базе"""
    client_id: str
    """ID клиента"""
    team_id: int
    """ID команды"""
    priority: int
    """Приоритет аккаунта"""
    created_at: datetime
    """Время создания приоритета"""
    updated_at: datetime
    """Время обновления приоритета"""
