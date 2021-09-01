from dataclasses import dataclass
from typing import Optional
from external_offers.entities.response import BasicResponse
from external_offers.enums.user_segment import UserSegment
from external_offers.enums.teams import TeamSettings


@dataclass
class Team:
    id: int
    """ ID команды """
    name: str
    """ Название команды """
    segment: Optional[UserSegment]
    """ Сегмент пользователей, которые выдаются команде  """
    settings: Optional[TeamSettings]
    """
    Настройки команды, которые используются для
    - фильтрации обьявлений
    - фильтрации пользователей,
    - сортировки заданий
    - параметров выдаваемого пакета
    """


@dataclass
class Operator:
    id: int
    """ ID оператора """
    name: Optional[str] = None
    """Имя оператора """
    team_id: Optional[int] = None
    """ ID команды оператора """
    role_id: Optional[int] = None
    """ ID роли оператора """
    is_teamlead: bool = False
    """ Является ли оператор тимлидом """


# TODO: возможно в будущем отказаться от отдельой таблички с 
# ролями, и хранить роли из ручки в строковом поле в табличке оператора.
# в таком случае в админке будут храниться только те роли, которые
# существуют на циане, и нельзя будет создать внутренние админочные роли.
@dataclass
class Role:
    id: int
    """ ID роли """
    name: str
    """ Название роли """


@dataclass
class UpdateOperatorNameRequest:
    name: str
    """Имя оператора"""

@dataclass
class UpdateOperatorNameResponse(BasicResponse):
    pass


# @dataclass
# class UpdateOperatorTeamRequest:
#     team_id: int
#     """ ID команды, в которую нужно добавить оператора """
#     operator_id: int
#     """ ID оператора, которого нужно добавить в команду """


# @dataclass
# class UpdateTeamSegmentRequest:
#     team_id: int
#     """ ID команды, у которой нужно поменять сегмент"""
#     segment: UserSegment
#     """ Сегмент пользователя """


@dataclass
class CreateTeamRequest:
    name: str
    """Название команды"""


# @dataclass
# class UpdateOperatorTeamResponse(BasicResponse):
#     pass


# @dataclass
# class UpdateTeamSegmentResponse(BasicResponse):
#     pass


@dataclass
class CreateTeamResponse(BasicResponse):
    pass
