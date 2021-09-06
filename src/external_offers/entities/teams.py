from dataclasses import dataclass
from typing import Optional
from external_offers.enums.user_segment import UserSegment
from external_offers.enums.teams import TeamSettings


@dataclass
class Team:
    id: str
    """ ID команды """
    name: str
    """Название команды """
    lead_id: str
    """ ID лида команды """
    segment: Optional[UserSegment] = None
    """ Сегмент пользователей, которых будет обрабатывать команда """
    settings: Optional[TeamSettings] = None
    """Настройки команды"""


@dataclass
class CreateTeamRequest:
    name: str
    """Название команды"""
    lead_id: str
    """ ID лида команды """
    segment: Optional[UserSegment] = None
    """ Сегмент пользователей, которых будет обрабатывать команда """
    settings: Optional[TeamSettings] = None
    """Настройки команды"""


@dataclass
class UpdateTeamRequest:
    id: str
    """ ID команды"""
    lead_id: str
    """ ID лида команды """
    name: str
    """Название команды"""
    segment: Optional[UserSegment] = None
    """ Сегмент пользователей, которых будет обрабатывать команда """
    settings: Optional[TeamSettings] = None
    """Настройки команды"""


@dataclass
class DeleteTeamRequest:
    id: str
    """ID команды которую нужно удалить"""


# TODO: возможно в будущем отказаться от отдельой таблички с 
# ролями, и хранить роли из ручки в строковом поле в табличке оператора.
# в таком случае в админке будут храниться только те роли, которые
# существуют на циане, и нельзя будет создать внутренние админочные роли.
@dataclass
class Role:
    id: str
    """ ID роли """
    name: str
    """ Название роли """
