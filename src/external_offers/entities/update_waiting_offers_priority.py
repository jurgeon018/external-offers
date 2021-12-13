from dataclasses import dataclass
from typing import Optional


@dataclass
class PrioritizeWaitingOffersRequest:
    is_test: bool
    team_id: Optional[str] = None
