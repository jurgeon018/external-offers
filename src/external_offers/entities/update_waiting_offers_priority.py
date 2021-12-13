from dataclasses import dataclass
from typing import Optional


@dataclass
class PrioritizeWaitingOffersRequest:
    team_id: Optional[str] = None
    is_test: bool = True
