from dataclasses import dataclass


@dataclass
class CreateTestOfferRequest:
    client_id: str
    """ID клиента к которому присвоится задание"""
    id: str
    """Уникальный ключ"""
    source_object_id: str
    """ID объявления на внешней площадке"""
    source_object_model: dict
    """Данные об объявлении"""
    is_calltracking: bool
    """Есть ли коллтрекинг у объявления"""
    timestamp: datetime
    """Дата отправки"""
    synced: bool
    """Синхронизировано ли объявление с таблицей заданий"""
    created_at: datetime
    """Дата создания записи в базе"""
    updated_at: datetime
    """Дата обновления записи в базе"""
    source_user_id: Optional[str] = None
    """ID пользователя на внешней площадке"""
    user_segment: Optional[UserSegment] = None
    """Сегмент пользователя"""


@dataclass
class CreateTestOfferResponse:
    pass

