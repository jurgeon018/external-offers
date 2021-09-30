from dataclasses import dataclass
import json
from typing import Optional

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
    settings: dict
    """Настройки команды"""
    full_name: Optional[str] = None
    """Имя оператора """
    team_id: Optional[int] = None
    """ ID команды оператора """
    is_teamlead: bool = False
    """ Имеет ли право быть лидом команд """
    segment: Optional[UserSegment] = None
    """Сегмент пользователей, которых будет обрабатывать команда"""

    def get_settings(self):
        settings = {}    
        if self.settings:
            settings = json.loads(self.settings)
        return settings


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
