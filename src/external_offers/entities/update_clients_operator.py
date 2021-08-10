from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateClientsOperatorRequest:
    old_operator_id: int
    new_operator_id: int


@dataclass
class UpdateClientsOperatorResponse:
    success: bool
    message: Optional[str] = None
