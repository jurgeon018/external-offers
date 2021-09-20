from dataclasses import dataclass
from typing import Optional

from external_offers.enums.teams import TeamSettings
from external_offers.enums.user_segment import UserSegment


@dataclass
class Operator:
    operator_id: str
    """ ID оператора """
    full_name: Optional[str] = None
    """Имя оператора """
    team_id: Optional[int] = None
    """ ID команды оператора """
    is_teamlead: bool = False
    """ Имеет ли право быть лидом команд """


@dataclass
class EnrichedOperator:
    operator_id: str
    """ ID оператора """
    team_name: str
    """Название команды"""
    lead_id: str
    """ID лида команды"""
    full_name: Optional[str] = None
    """Имя оператора """
    team_id: Optional[int] = None
    """ ID команды оператора """
    is_teamlead: bool = False
    """ Имеет ли право быть лидом команд """
    segment: Optional[UserSegment] = None
    """Сегмент пользователей, которых будет обрабатывать команда"""
    settings: Optional[TeamSettings] = None
    """Настройки команды"""


@dataclass
class CreateOperatorRequest:
    operator_id: str
    """ID оператора"""
    full_name: str
    """ Имя оператора"""
    team_id: Optional[int] = None
    """ID команды"""


@dataclass
class UpdateOperatorRequest:
    operator_id: str
    """ID оператора"""
    full_name: str
    """Имя оператора"""
    team_id: Optional[int] = None
    """ID команды"""


@dataclass
class DeleteOperatorRequest:
    operator_id: str
    """ID оператора которого нужно удалить"""
