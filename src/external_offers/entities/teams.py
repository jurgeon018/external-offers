from dataclasses import dataclass
from typing import Any, Optional

from cian_json import json

from external_offers.enums.teams import TeamType


@dataclass
class OffersSettings:
    """Настройки фильтрации обьявлений"""
    categories: Optional[list[str]] = None
    """Категории"""
    regions: Optional[list[str]] = None
    """Регионы"""


@dataclass
class ClientsSettings:
    # Настройки фильтрации клиентов
    calltracking: bool = False
    """Флаг колтрекинга"""
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


@dataclass
class PrioritySettings:
    """
    Настройки приоритетов в очереди
    Приоритет собирается из 7 частей в число равной длины для всех заданий(для сквозной сортировки)
    1-5 - части приоритета для клиента
    """
    # 1 часть - тип клиента: добивочный клиент с неактивированым черновиком, новый клиент
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
    # TODO: https://jira.cian.tech/browse/CD-116917
    """Настройки промокодов"""
    promocode_polygons: Optional[list[str]] = None
    """Регионы применения(айдишники полигонов)"""
    regions_with_paid_publication: Optional[list[str]] = None
    """Регионы применения(айдишники регионов)"""
    filling: Optional[list[str]] = None
    """Наполнение"""
    promocode_price: int = 0
    """Стоимость"""
    promocode_period: Optional[str] = None
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
class Team:
    team_id: int
    """ID команды"""
    team_name: str
    """Название команды"""
    lead_id: str
    """ID лида команды"""
    settings: str
    """Настройки команды"""
    team_type: Optional[TeamType] = TeamType.attractor.value

    def get_settings(self) -> dict:
        settings = {}
        if self.settings:
            json_settings = json.loads(self.settings)
            settings = json_settings
        return settings


@dataclass
class StrTeamSettings:
    categories: str = '[]'
    """Категории"""
    regions: str = '[]'
    """Регионы"""
    segments: str = '[]'
    """Сегменты"""
    subsegments: str = '[]'
    """Субсегменты"""
    promocode_polygons: str = '[]'
    """ID полигонов"""
    regions_with_paid_publication: str = '[]'
    """ID регионов"""
    filling: str = '[]'
    """Категории"""
    main_regions_priority: str = '{}'
    """Категории"""


@dataclass
class CreateTeamRequest:
    team_name: str
    """Название команды"""
    lead_id: str
    """ID лида команды"""
    team_type: TeamType
    """Тип команды"""


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
    # StrTeamSettings должен быть в самом верху, чтобы перебить свойства из TeamSettings
    StrTeamSettings,
    TeamSettings,
    _UpdateTeamRequest,
    # _UpdateTeamRequest должен быть в самом низу, чтобы не получить ошибку
    # TypeError: non-default argument 'team_id' follows default argument
):
    pass


@dataclass
class DeleteTeamRequest:
    team_id: int
    """ID команды которую нужно удалить"""


@dataclass
class TeamInfo:
    team_id: str
    """Идентификатор команды"""
    team_settings: dict
    """Настройки команды"""
    team_type: TeamType
    """Тип команды"""
