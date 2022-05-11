from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional

from external_offers.enums.teams import TeamType
from external_offers.enums.user_segment import UserSegment


@dataclass
class Operator:
    operator_id: str
    """ ID оператора """
    created_at: datetime
    """Дата создания оператора"""
    updated_at: datetime
    """Дата обновления оператора"""
    full_name: Optional[str] = None
    """Имя оператора """
    team_id: Optional[int] = None
    """ ID команды оператора """
    is_teamlead: bool = False
    """ Имеет ли право быть лидом команд """
    email: Optional[str] = None
    """Email оператора"""


@dataclass
class EnrichedOperator:
    operator_id: str
    """ ID оператора """
    team_name: str
    """Название команды"""
    lead_id: str
    """ID лида команды"""
    settings: dict[str, Any]
    """Настройки команды"""
    created_at: datetime
    """Дата создания оператора"""
    updated_at: datetime
    """Дата обновления оператора"""
    team_type: TeamType
    """Тип команды"""
    full_name: Optional[str] = None
    """Имя оператора """
    email: Optional[str] = None
    """Email оператора"""
    team_id: Optional[int] = None
    """ ID команды оператора """
    is_teamlead: bool = False
    """ Имеет ли право быть лидом команд """
    segment: Optional[UserSegment] = None
    """Сегмент пользователей, которых будет обрабатывать команда"""
    team_waiting_offers_count: Optional[int] = None
    """Количество заданий в ожидании в очереди команды"""
    team_waiting_offers_count_updated_at: Optional[datetime] = None
    """Время последнего обновления количества заданий в ожидании в очереди команды"""
    team_division: Optional[str] = None
    """Название групы номеров"""


@dataclass
class CreateOperatorRequest:
    operator_id: str
    """ID оператора"""


@dataclass
class UpdateOperatorRequest:
    operator_id: str
    """ID оператора"""
    full_name: str
    """Имя оператора"""
    team_id: Optional[int] = None
    """ID команды"""
    email: Optional[str] = None
    """Email оператора"""


@dataclass
class UpdateOperatorsRequest:
    pass


@dataclass
class DeleteOperatorRequest:
    operator_id: str
    """ID оператора которого нужно удалить"""
