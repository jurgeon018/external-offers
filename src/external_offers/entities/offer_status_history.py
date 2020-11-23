from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OfferStatusHistory:
    id: int
    """Идентификатор элемента истории"""
    offer_id: str
    """Идентификатор объявления"""
    operator_id: int
    """Оператор, на которого было назначено объявление при переходе"""
    created_at: datetime
    """Дата создания нового статуса"""
    status: str
    """Статус объявления"""
    previous_status: Optional[str] = None
    """Предыдущий статус объявления"""
