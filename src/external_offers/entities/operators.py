from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Operator:
    id: str
    """ ID оператора """
    name: Optional[str] = None
    """Имя оператора """
    team_id: Optional[str] = None
    """ ID команды оператора """
    is_teamlead: bool = False
    """ Имеет ли право быть лидом команд """


@dataclass
class CreateOperatorRequest:
    id: str
    """ID оператора"""
    name: str
    """ Имя оператора"""
    team_id: Optional[str] = None
    """ID команды"""


@dataclass
class UpdateOperatorRequest:
    id: str
    """ID оператора"""
    name: str
    """Имя оператора"""
    team_id: Optional[str] = None
    """ID команды"""


@dataclass
class DeleteOperatorRequest:
    id: str
    """ID оператора которого нужно удалить"""
    

@dataclass
class UpdateOperatorsTeamRequest:
    team_id: str
    """ ID команды, в которую нужно добавить операторов """
    operators_id: Optional[List[str]] = None
    """ ID операторов, которых нужно добавить в команду """
