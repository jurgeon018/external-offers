from dataclasses import dataclass
from typing import Optional


@dataclass
class PrioritizeWaitingOffersRequest:
    team_id: Optional[int] = None
