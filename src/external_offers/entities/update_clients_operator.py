from dataclasses import dataclass
from typing import Optional


@dataclass
class UpdateClientsOperatorRequest:
    old_operator_id: int
    """ID старого оператора, с которого нужно перекинуть задания"""
    new_operator_id: int
    """ID нового оператора, на которого нужно перекинуть задания"""


@dataclass
class UpdateClientsOperatorResponse:
    success: bool
    """Статус операции"""
    message: Optional[str] = None
    """Текст ответа"""
