
from dataclasses import dataclass
from typing import Optional


@dataclass
class AccountPriorities:
    smb_account_priority: int
    """Приоритет агента"""
    homeowner_account_priority: int
    """Приоритет собственника"""
    new_cian_user_id: Optional[int] = None
    """Идентификатор нового пользователя на циане"""
