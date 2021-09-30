import json
from dataclasses import dataclass
from typing import Optional

from external_offers.enums.user_segment import UserSegment


@dataclass
class Team:
    team_id: int
    """ID команды"""
    team_name: str
    """Название команды"""
    lead_id: str
    """ID лида команды"""
    settings: dict
    """Настройки команды"""

    def get_settings(self):
        settings = {}    
        if self.settings:
            settings = json.loads(self.settings)
        return settings


@dataclass
class CreateTeamRequest:
    team_name: str
    """Название команды"""
    lead_id: str
    """ ID лида команды """


@dataclass
class OffersSettings:
    """Настройки фильтрации обьявлений"""
    categories: Optional[list[str]] = None
    """Категории"""
    regions: Optional[list[str]] = None
    """Регионы"""

    """todo минимальная дата создания в очереди"""
    
    """todo флаг коллтрекинга"""


@dataclass
class ClientsSettings:

    # Настройки фильтрации клиентов
    segments: Optional[list[str]] = None
    """Сегменты пользователей, которых будет обрабатывать команда"""
    subsegments: Optional[list[str]] = None
    """Субсегменты пользователей, которых будет обрабатывать команда"""
    unique_objects_min: Optional[int] = None
    """Количество уникальных объектов, которых нет на Циан"""
    unique_objects_max: Optional[int] = None
    """Количество уникальных объектов, которых нет на Циан"""
    commercial_objects_percentage_min: Optional[int] = None
    """% коммерческих объектов от общего числа объектов"""
    commercial_objects_percentage_max: Optional[int] = None
    """% коммерческих объектов от общего числа объектов"""
    suburban_objects_percentage_min: Optional[int] = None
    """% загородных объектов от общего числа объектов"""
    suburban_objects_percentage_max: Optional[int] = None
    """% загородных объектов от общего числа объектов"""
    avito_objects_percentage_max: Optional[int] = None
    """% обьектов с площадки 'avito'"""
    avito_objects_percentage_min: Optional[int] = None
    """% обьектов с площадки 'avito'"""
    domclick_objects_percentage_max: Optional[int] = None
    """% обьектов с площадки 'domclick'"""
    domclick_objects_percentage_min: Optional[int] = None
    """% обьектов с площадки 'domclick'"""
    yandex_objects_percentage_max: Optional[int] = None
    """% обьектов с площадки 'yandex'"""
    yandex_objects_percentage_min: Optional[int] = None
    """% обьектов с площадки 'yandex'"""
    valid_days_after_call: Optional[int] = None
    """уже был в обзвоне"""

    """Минимальная дата создания в очереди"""
    calltracking: bool = True
    """Флаг колтрекинга"""

@dataclass
class PrioritySettings:
    """
    Настройки приоритетов в очереди
    Приоритет собирается из 7 частей в число равной длины для всех заданий(для сквозной сортировки)
    1-5 - части приоритета для клиента
    1 часть - тип клиента: добивочный клиент с неактивированым черновиком, новый клиент
    """
    activation_status_position: int = 1
    """Порядок признака 'Статус клиента(добивочный или новый)'"""
    unactivated_client_priority: int = 1
    """Приоритет добивочного клиента"""
    new_client_priority: int = 2
    """Приоритет нового клиента"""
    # 2 часть - статус звонка, все новые задания идут с приоритетом 3 в начале, недозвоны - 2, перезвоны - 1
    call_status_position: int = 2
    """Порядок признака 'Cтатус звонка'"""
    call_later_priority: int = 1
    """Приоритет перезвонов"""
    call_missed_priority: int = 2
    """Приоритет недозвонов"""
    waiting_priority: int = 3
    """Приоритет ожидающих"""
    # 3 часть - регион, основные регионы из ключей настройки ниже ранжируются по значениям, остальные - все вместе
    region_position: int = 3
    """Порядок признака 'Регион'"""
    main_regions_priority: Optional[dict[str, int]] = None
    """Приоритет регионов"""
    # 4 часть - сегмент - собственник или smb
    segment_position: int = 4
    """Порядок признака 'Сегмент'"""
    smb_priority: int = 1
    """Приоритет для сегмента SMB"""
    homeowner_priority: int = 2
    """Приоритет для сегмента собственников"""
    # 5 часть - статус учетной записи - нет лк на Циан, нет активных объявлений, соблюдена пропорция заданий в админке
    # и уже активных объявлений у клиента, для smb дополнительный приоритет - активный лк
    lk_position: int = 5
    """Порядок признака 'Статус Учетной Записи(наличие учетной записи и количество обьявлений'"""
    no_lk_smb_priority: int = 1
    """Нет ЛК на циан"""
    no_active_smb_priority: int = 2
    """нет активных объявлений"""
    keep_proportion_smb_priority: int = 3
    """соблюдена пропорция заданий в админке и уже активных объявлений у клиента"""
    no_lk_homeowner_priority: int = 1
    """Приоритет для smb: нет ЛК на циан"""
    active_lk_homeowner_priority: int = 2
    """Приоритет для smb: есть активный ЛК на циан"""
    # 6-7 - части приоритета для обьявления
    # 6 часть - тип сделки - продажа, аренда
    deal_type_position: int = 6
    """Порядок признака 'Тип сделки'"""
    sale_priority: int = 1
    """Приоритет продажи"""
    rent_priority: int = 2
    """Приоритет аренды"""
    # 7 часть - тип недвижимости - городская, загородная, комерческая
    offer_type_position: int = 7
    """Порядок признака 'Тип Недвижимости'"""
    flat_priority: int = 1
    """Приоритет городской недвижимости"""
    suburban_priority: int = 2
    """Приоритет загородной недвижимости"""
    commercial_priority: int = 3
    """Приоритет комерческой недвижимости"""
    # 8 часть - ???
    creation_date_position: int = 8
    """Порядок признака 'Дата Создания'"""
    # 9 часть - ???
    commercial_position: int = 9
    """Порядок признака 'Доля Комерческих Обьектов'"""
    # 10 часть - ???
    subsegment_position: int = 10
    """Порядок признака 'Субсегмент'"""


@dataclass
class PromocodeSettings:
    """Настройки промокодов"""
    promocode_regions: Optional[list[str]] = None
    """Регионы применения"""
    filling: Optional[list[str]] = None
    """Наполнение"""
    promocode_price: int = 0
    """Стоимость"""
    promocode_period: int = 30
    """Срок действия промокодов"""
    promocode_group_name: Optional[str] = None
    """Название групы промокодов"""


@dataclass
class TeamSettings(
    OffersSettings,
    ClientsSettings,
    PrioritySettings,
    PromocodeSettings,
):
    pass


@dataclass
class _UpdateTeamRequest:
    team_id: int
    """ID команды"""
    lead_id: str
    """ID лида команды """
    team_name: str
    """Название команды"""


@dataclass
class UpdateTeamRequest(
    TeamSettings,
    _UpdateTeamRequest,
):
    pass


@dataclass
class DeleteTeamRequest:
    team_id: int
    """ID команды которую нужно удалить"""
