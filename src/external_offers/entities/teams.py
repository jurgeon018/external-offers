
from typing import Optional
from dataclass import dataclass


@dataclass
class UpdateOperatorTeamRequest:
    team_id: int
    """ Идентификатор команды, в которую нужно добавить оператора """
    operator_id: int
    """ Идентификатор оператора, которого нужно добавить в команду """


@dataclass
class UpdateOperatorTeamResponse:
    success: bool
    """ Статус операции """
    message: Optional[str] = None
    """ Текст ответа """

