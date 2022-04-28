from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from external_offers.entities.client.update_client_reason_of_decline import ReasonOfDeclineEnum
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
    real_phone: Optional[str] = None
    """Добытый реальный телефон клиента"""
    real_name: Optional[str] = None
    """Добытое настоящее ФИО клиента"""
    real_phone_hunted_at: Optional[datetime] = None
    """Дата добычи реального телефона клиента"""
    client_name: Optional[str] = None
    """Имя клиента"""
    cian_user_id: Optional[int] = None
    """Идентификатор пользователя на Циане"""
    client_email: Optional[str] = None
    """Почтовый ящик клиента, к которому привязана учетная запись Циана"""
    operator_user_id: Optional[str] = None
    """Идентификатор оператора, который взял клиента в работу"""
    hunter_user_id: Optional[str] = None
    """Идентификатор оператора, который получил реальные данные клиента"""
    team_id: Optional[int] = None
    """Идентификатор команды, в которой находился оператор"""
    segment: Optional[UserSegment] = None
    """Сегмент пользователя"""
    subsegment: Optional[str] = None
    """Субсегмент пользователя"""
    last_call_id: Optional[str] = None
    """Последний идентификатор звонка"""
    calls_count: int = 0
    """Количество звонков"""
    main_account_chosen: bool = False
    """Флаг выбора главного аккаунта(аккаунт выбранный при первом сохранении черновика)"""
    unactivated: bool = False
    """Флаг добивочного клиента с неактивированым черновиком(нужен для разделения обычных и добивочных клиентов)"""
    drafted_at: Optional[datetime] = None
    """Время предразмещения обьявления операторов(время становления клиента добивочным)"""
    activated_at: Optional[datetime] = None
    """Время активации обьявления клиентом"""
    comment: Optional[str] = None
    """Коментарий к карточке от оператора"""
    reason_of_decline: Optional[ReasonOfDeclineEnum] = None
    """Причина отказа"""
    additional_numbers: Optional[str] = None
    """Дополнительные тел. номера"""
    additional_emails: Optional[str] = None
    """Дополнительные почты"""
    next_call: Optional[datetime] = None
    """Дата следующего звонка клиенту"""
    is_test: bool = False
    """Тестовое обьявление"""


@dataclass
class ClientWaitingOffersCount:
    client_id: str
    """Идентификатор клиента"""
    parsed_id: str
    """Идентификатор обьявления"""
    waiting_offers_count: int
    """Количество объявлений в ожидании"""


@dataclass
class ClientDraftOffersCount:
    client_id: str
    """Идентификатор клиента"""
    draft_offers_count: int
    """Количество неактивированых черновиков"""
    priority: int
    """Старый приоритет клиента, который был ему проставлен в момент когда он еще не был добивочным"""
    team_priorities: Optional[str] = None
    """ Старые командные приоритеты клиента, которые были ему проставлены в момент когда он еще не был добивочным"""


@dataclass
class ClientAccountInfo:
    cian_user_id: int
    """Идентификатор клиента на Циане"""
    email: Optional[str]
    """Почта привязанная к аккаунту"""
    is_agent: bool
    """Агентский ли аккаунт"""
