from dataclasses import dataclass
from typing import Optional

from external_offers.repositories.users.entities import UserModelV2


@dataclass
class ClientChooseMainProfileResult:
    has_bad_account: bool
    """Есть неподходящий для добавления в очередь аккаунт"""
    chosen_profile: Optional[UserModelV2]
    """Модель профиля"""


@dataclass
class HomeownerClientChooseMainProfileResult(ClientChooseMainProfileResult):
    has_wrong_user_source_type: bool
    """Есть неподходящий тип источника, который нужно отфильтровать"""


@dataclass
class SmbClientChooseMainProfileResult(ClientChooseMainProfileResult):
    has_wrong_user_source_type: bool
    """Есть неподходящий тип источника, который нужно отфильтровать"""
