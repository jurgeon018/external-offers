from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from external_offers.enums.user_segment import UserSegment


@dataclass
class ParsedOffer:
    id: str
    """Уникальный ключ"""
    source_object_id: str
    """ID объявления на внешней площадке"""
    source_user_id: str
    """ID пользователя на внешней площадке"""
    source_object_model: dict
    """Данные об объявлении"""
    is_calltracking: bool
    """Есть ли коллтрекинг у объявления"""
    timestamp: datetime
    """Дата отправки"""
    user_segment: Optional[UserSegment] = None
    """Сегмент пользователя"""
