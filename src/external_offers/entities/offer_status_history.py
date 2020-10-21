from dataclasses import dataclass
from datetime import datetime


@dataclass
class OfferStatusHistory:
    id: int
    'Идентификатор элемента истории'
    offer_id: int
    'Идентификатор объявления'
    operator_id: int
    'Оператор, на которого было назначено объявление при переходе'
    previous_status: str
    'Предыдущий статус объявления'
    status: str
    'Статус объявления'
    created_at: datetime
    'Дата создания нового статуса'
