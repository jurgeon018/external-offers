import json
from dataclasses import asdict
from typing import Any

from asyncpg.exceptions import PostgresError, UniqueViolationError
from cian_core.runtime_settings import runtime_settings

from external_offers.entities.response import BasicResponse
from external_offers.entities.teams import (
    CreateTeamRequest,
    DeleteTeamRequest,
    GetWaitingOffersCountForTeam,
    StrTeamSettings,
    TeamSettings,
    UpdateTeamRequest,
)
from external_offers.repositories.monolith_cian_service.entities.service_package_strategy_item_model import (
    DurationInDays,
)
from external_offers.repositories.postgresql.teams import create_team, delete_team_by_id, get_offers_count_for_team, update_team_by_id


def build_default_team_settings() -> dict[str, Any]:
    offers_settings = {
        'categories': runtime_settings.OFFER_TASK_CREATION_CATEGORIES,
        'regions': runtime_settings.OFFER_TASK_CREATION_REGIONS,
    }
    clients_settings = {
        'segments': runtime_settings.OFFER_TASK_CREATION_SEGMENTS,
        'subsegments': [],
        # TODO: https://jira.cian.tech/browse/CD-116416
        # '???': runtime_settings.OFFER_TASK_CREATION_MINIMUM_OFFERS,
        # '???': runtime_settings.OFFER_TASK_CREATION_MAXIMUM_OFFERS,
        # 'unique_objects_min': ...,
        # 'unique_objects_max': ...,
        # 'commercial_objects_percentage_min': ...,
        # 'commercial_objects_percentage_max': ...,
        # 'suburban_objects_percentage_min': ...,
        # 'suburban_objects_percentage_max': ...,
        # 'avito_objects_percentage_max': ...,
        # 'avito_objects_percentage_min': ...,
        # 'domclick_objects_percentage_max': ...,
        # 'domclick_objects_percentage_min': ...,
        # 'yandex_objects_percentage_max': ...,
        # 'yandex_objects_percentage_min': ...,
        # 'valid_days_after_call': ...,
    }
    priority_settings = {
        # 1 часть - тип клиента: добивочный клиент с неактивированым черновиком - 1, новый клиент - 2
        'activation_status_position': 1,
        'unactivated_client_priority': runtime_settings.UNACTIVATED_CLIENT_PRIORITY,
        'new_client_priority': runtime_settings.NEW_CLIENT_PRIORITY,
        # 2 часть - статус звонка, все новые задания идут с приоритетом 3 в начале, недозвоны - 2, перезвоны - 1
        'call_status_position': 2,
        'call_later_priority': runtime_settings.CALL_LATER_PRIORITY,
        'call_missed_priority': runtime_settings.CALL_MISSED_PRIORITY,
        'waiting_priority': runtime_settings.WAITING_PRIORITY,
        # 3 часть - регион, основные регионы из ключей настройки ниже ранжируются по значениям, остальные - все вместе
        'region_position': 3,
        'main_regions_priority': runtime_settings.MAIN_REGIONS_PRIORITY,
        # 4 часть - сегмент - собственник или smb
        'segment_position': 4,
        'smb_priority': runtime_settings.SMB_PRIORITY,
        'homeowner_priority': runtime_settings.HOMEOWNER_PRIORITY,
        # 5 часть - статус учетной записи - нет лк на Циан,нет активных объявлений,соблюдена пропорция заданий в админке
        # и уже активных объявлений у клиента, для smb дополнительный приоритет - активный лк
        'lk_position': 5,
        'no_lk_smb_priority': runtime_settings.NO_LK_SMB_PRIORITY,
        'no_active_smb_priority': runtime_settings.NO_ACTIVE_SMB_PRIORITY,
        'keep_proportion_smb_priority': runtime_settings.KEEP_PROPORTION_SMB_PRIORITY,
        'no_lk_homeowner_priority': runtime_settings.NO_LK_HOMEOWNER_PRIORITY,
        'active_lk_homeowner_priority': runtime_settings.ACTIVE_LK_HOMEOWNER_PRIORITY,
        # 6-7 - части приоритета для обьявления
        # 6 часть - тип сделки - продажа, аренда
        'deal_type_position': 6,
        'sale_priority': runtime_settings.SALE_PRIORITY,
        'rent_priority': runtime_settings.RENT_PRIORITY,
        # 7 часть - тип недвижимости - городская, загородная, комерческая
        'offer_type_position': 7,
        'flat_priority': runtime_settings.FLAT_PRIORITY,
        'suburban_priority': runtime_settings.SUBURBAN_PRIORITY,
        'commercial_priority': runtime_settings.COMMERCIAL_PRIORITY,
        # 'creation_date_position': ...,
        # 'commercial_position': ...,
        # 'subsegment_position': ...,
    }
    promocode_settings = {
        'promocode_polygons': runtime_settings.PROMOCODE_POLYGONS,
        'regions_with_paid_publication': runtime_settings.REGIONS_WITH_PAID_PUBLICATION,
        # TODO: https://jira.cian.tech/browse/CD-116917
        'filling': [],
        # 'promocode_price': ...,
        'promocode_period': DurationInDays.thirty.value,
        'promocode_group_name': runtime_settings.PROMOCODE_GROUP_NAME,
    }
    settings = asdict(TeamSettings(
        **offers_settings,
        **clients_settings,
        **priority_settings,
        **promocode_settings,
    ))
    return settings


async def create_team_public(request: CreateTeamRequest, user_id: int) -> BasicResponse:
    success = False
    settings = build_default_team_settings()
    try:
        await create_team(
            team_name=request.team_name,
            lead_id=request.lead_id,
            settings=settings,
            team_type=request.team_type,
        )
        success = True
        message = 'Команда была успешно создана.'
    except UniqueViolationError as e:
        message = f'Такая команда уже существует: {e}'
    except PostgresError as e:
        message = f'Во время создания команды произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )


async def update_team_public(request: UpdateTeamRequest, user_id: int) -> BasicResponse:
    success = False
    settings = asdict(request)
    del settings['team_id']
    del settings['team_name']
    del settings['lead_id']
    for key, value in settings.items():
        if key in asdict(StrTeamSettings()).keys():
            settings[key] = json.loads(value)
    try:
        await update_team_by_id(
            team_id=request.team_id,
            team_name=request.team_name,
            lead_id=request.lead_id,
            settings=settings,
        )
        success = True
        message = 'Информация про команду была успешно обновлена.'
    except PostgresError as e:
        message = f'Во время обновления команды произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )


async def delete_team_public(request: DeleteTeamRequest, user_id: int) -> BasicResponse:
    success = False
    try:
        await delete_team_by_id(team_id=request.team_id)
        success = True
        message = 'Команда была успешно удалена.'
    except PostgresError as e:
        message = f'Во время удаления команды произошла ошибка: {e}'
    return BasicResponse(
        success=success,
        message=message,
    )


async def get_waiting_offers_count_for_team_public(request: GetWaitingOffersCountForTeam, user_id: int) -> BasicResponse:
    offers_count = await get_offers_count_for_team(team_id=request.team_id)
    return BasicResponse(
        success=True,
        message=f'Количество обьявлений в очереди для команды №{request.team_id} - {offers_count}'
    )
