from dataclasses import dataclass
from typing import Optional


@dataclass
class BasicResponse:
    success: bool
    """ Статус операции """
    message: Optional[str] = None
    """ Текст ответа """
