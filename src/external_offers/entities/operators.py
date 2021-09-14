from dataclasses import dataclass
from typing import Optional


@dataclass
class Operator:
    operator_id: str
    """ ID оператора """
    name: Optional[str] = None
    """Имя оператора """
    team_id: Optional[str] = None
    """ ID команды оператора """
    is_teamlead: bool = False
    """ Имеет ли право быть лидом команд """


@dataclass
class CreateOperatorRequest:
    operator_id: str
    """ID оператора"""
    name: str
    """ Имя оператора"""
    team_id: Optional[str] = None
    """ID команды"""


@dataclass
class UpdateOperatorRequest:
    operator_id: str
    """ID оператора"""
    name: str
    """Имя оператора"""
    team_id: Optional[str] = None
    """ID команды"""


@dataclass
class DeleteOperatorRequest:
    operator_id: str
    """ID оператора которого нужно удалить"""
