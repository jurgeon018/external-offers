from dataclasses import dataclass
from typing import Optional


@dataclass
class PrioritizeWaitingOffersRequest:
    team_id: str
    is_test: Optional[bool] = None
