from dataclasses import dataclass
from typing import Optional

from external_offers.enums.teams import TeamSettings
from external_offers.enums.user_segment import UserSegment


@dataclass
class Team:
    team_id: str
    """ID команды"""
    name: str
    """Название команды"""
    lead_id: str
    """ID лида команды"""
    segment: Optional[UserSegment] = None
    """Сегмент пользователей, которых будет обрабатывать команда"""
    settings: Optional[TeamSettings] = None
    """Настройки команды"""


@dataclass
class CreateTeamRequest:
    name: str
    """Название команды"""
    lead_id: str
    """ ID лида команды """
    segment: Optional[UserSegment] = None
    """Сегмент пользователей, которых будет обрабатывать команда"""
    settings: Optional[TeamSettings] = None
    """Настройки команды"""


@dataclass
class UpdateTeamRequest:
    team_id: str
    """ID команды"""
    lead_id: str
    """ID лида команды """
    name: str
    """Название команды"""
    segment: Optional[UserSegment] = None
    """Сегмент пользователей, которых будет обрабатывать команда"""
    settings: Optional[TeamSettings] = None
    """Настройки команды"""


@dataclass
class DeleteTeamRequest:
    team_id: str
    """ID команды которую нужно удалить"""
