from dataclass import dataclass
from typing import Optional
from external_offers.entities.response import BasicResponse
from external_offers.enums.user_segment import UserSegment


@dataclass
class Team:
    id: int
    """ ID команды """
    name: str
    """ Название команды """
    segment: Optional[UserSegment]
    """ Сегмент пользователей, которые выдаются команде  """
    settings: dict
    """
    Настройки команды, которые используются для
    - фильтрации обьявлений
    - фильтрации пользователей,
    - сортировки заданий
    - параметров выдаваемого пакета
    """


@dataclass
class Role:
    id: int
    """ ID роли """
    name: str
    """ Название роли """


@dataclass
class Operator:
    id: int
    """ ID оператора """
    role_id: int
    """ ID роли оператора """
    team_id: int
    """ ID команды оператора """
    name: str
    """Имя оператора """
    is_teamlead: bool = False
    """ Является ли оператор тимлидом """


@dataclass
class UpdateOperatorTeamRequest:
    team_id: int
    """ Идентификатор команды, в которую нужно добавить оператора """
    operator_id: int
    """ Идентификатор оператора, которого нужно добавить в команду """


@dataclass
class UpdateOperatorTeamResponse(BasicResponse):
    pass


@dataclass
class UpdateTeamRoleRequest:
    team_id: int
    role_id: int


@dataclass
class UpdateTeamRoleResponse(BasicResponse):
    pass


@dataclass
class CreateTeamRequest:
    name: str
    """Название команды"""


@dataclass
class CreateTeamResponse(BasicResponse):
    pass
