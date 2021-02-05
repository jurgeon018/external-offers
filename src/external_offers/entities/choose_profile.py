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
    ...


@dataclass
class SmbClientChooseMainProfileResult(ClientChooseMainProfileResult):
    ...
    has_emls_or_subagent: bool
    """Есть ЕМЛС или саб аккаунт """