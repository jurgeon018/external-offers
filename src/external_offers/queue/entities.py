from dataclasses import dataclass
from datetime import datetime

from external_offers.repositories.monolith_cian_announcementapi.entities import ObjectModel


@dataclass
class SourceModel:
    source: str
    """Источник объявления"""
    source_object_id: str
    """Идентификатор объявления на сторонней площадке"""
    external_url: str
    """Ссылка объявления на сторонней площадке"""
    timestamp: datetime
    """Дата события получения модели"""


@dataclass
class AnnouncementMessage:
    source_model: SourceModel
    """Дополнительные поля"""
    model: ObjectModel
    """Объявление"""
    operation_id: str
    """Operation id"""
    date: datetime
    """Время отправки"""


@dataclass
class AnnouncementDeletedMessage:
    source_object_id: str
    """Идентификатор стороннего объявления"""
    operation_id: str
    """Operation id"""
    date: datetime
    """Время отправки"""
