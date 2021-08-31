from dataclass import dataclass
from typing import Optional


class BasicResponse:
    success: bool
    """ Статус операции """
    message: Optional[str] = None
    """ Текст ответа """
