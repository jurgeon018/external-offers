from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from external_offers.enums import ClientStatus, UserSegment


@dataclass
class Client:
    client_id: str
    """Идентификатор клиента"""
    avito_user_id: str
    """Идентификатор пользователя на Авито"""
    client_phones: List[str]
    """Телефон клиента"""
    status: ClientStatus
    """Статус клиента"""
    client_name: Optional[str] = None
    """Имя клиента"""
    cian_user_id: Optional[int] = None
    """Идентификатор пользователя на Циане"""
    client_email: Optional[str] = None
    """Почтовый ящик клиента, к которому привязана учетная запись Циана"""
    operator_user_id: Optional[str] = None
    """Идентификатор оператора, который взял клиента в работу"""
    segment: Optional[UserSegment] = None
    """Сегмент пользователя"""
    last_call_id: Optional[str] = None
    """Последний идентификатор звонка"""
    calls_count: int = 0
    """Количество звонков"""
    main_account_chosen: bool = False
    """Флаг выбора главного аккаунта(аккаунт выбранный при первом сохранении черновика)"""
    unactivated: bool = False
    """
    Флаг добивочного клиента с неактивированым черновиком
    (нужен для разделения недозвонов для обычных и добивочных клиентов)
    """
    comment: Optional[str] = None
    """Коментарий к карточке от оператора"""
    next_call: Optional[datetime] = None
    """Дата следующего звонка клиенту"""
    is_test: bool = False
    """Тестовое обьявление"""


@dataclass
class ClientWaitingOffersCount:
    client_id: str
    """Идентификатор клиента"""
    waiting_offers_count: int
    """Количество объявлений в ожидании"""


@dataclass
class ClientDraftOffersCount:
    client_id: str
    """Идентификатор клиента"""
    draft_offers_count: int
    """Количество неактивированых черновиков"""


@dataclass
class ClientAccountInfo:
    cian_user_id: int
    """Идентификатор клиента на Циане"""
    email: Optional[str]
    """Почта привязанная к аккаунту"""
    is_agent: bool
    """Агентский ли аккаунт"""
