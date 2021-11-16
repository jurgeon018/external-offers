from cian_entities.mappers import EntityMapper, ValueMapper

from external_offers.entities import EnrichedOperator, Operator, Team


teams_mapper = EntityMapper(
    Team,
    without_camelcase=True,
    mappers={
        'settings': ValueMapper(),
    }
)
operators_mapper = EntityMapper(
    Operator,
    without_camelcase=True,
    mappers={
        'created_at': ValueMapper(),
        'updated_at': ValueMapper(),
    }
)
enriched_operators_mapper = EntityMapper(
    EnrichedOperator,
    without_camelcase=True,
    mappers={
        'settings': ValueMapper(),
        'created_at': ValueMapper(),
        'updated_at': ValueMapper(),
    }
)
from external_offers.entities.teams import TeamSettings


OFFER_TASK_CREATION_CATEGORIES
COMMERCIAL_OFFER_TASK_CREATION_CATEGORIES

OFFER_TASK_CREATION_SEGMENTS
COMMERCIAL_OFFER_TASK_CREATION_SEGMENTS




team_settings_to_runtime_settings_mapping = {

    # # Настройки фильтрации обьявлений
    
    # TODO:
    'categories': 'OFFER_TASK_CREATION_CATEGORIES',
    # '???': 'COMMERCIAL_OFFER_TASK_CREATION_CATEGORIES',
    # TODO:
    # - перенести фильтрацию из set_synced_and_fetch_parsed_offers_chunk в prioritize_waiting_offers
    # - проставить 
    # - поменять настройки из рс на настройки из teams.settings
    # - прогнать старые тесты
    # - поправить старые тесты(если сломались)
    # - написать новые тесты(если нужно)
    'regions': 'OFFER_TASK_CREATION_REGIONS',

    # # Настройки фильтрации клиентов

    # TODO:
    'segments': 'OFFER_TASK_CREATION_SEGMENTS',
    # '???': 'COMMERCIAL_OFFER_TASK_CREATION_SEGMENTS',
    # 'subsegments': 'RS TODO',
    # '???': 'OFFER_TASK_CREATION_MINIMUM_OFFERS',
    # '???': 'OFFER_TASK_CREATION_MAXIMUM_OFFERS',
    # 'unique_objects_min': 'RS TODO',
    # 'unique_objects_max': 'RS TODO',
    # 'commercial_objects_percentage_min': 'RS TODO',
    # 'commercial_objects_percentage_max': 'RS TODO',
    # 'suburban_objects_percentage_min': 'RS TODO',
    # 'suburban_objects_percentage_max': 'RS TODO',
    # 'avito_objects_percentage_max': 'RS TODO',
    # 'avito_objects_percentage_min': 'RS TODO',
    # 'domclick_objects_percentage_max': 'RS TODO',
    # 'domclick_objects_percentage_min': 'RS TODO',
    # 'yandex_objects_percentage_max': 'RS TODO',
    # 'yandex_objects_percentage_min': 'RS TODO',
    # 'valid_days_after_call': 'RS TODO',
    # 'calltracking': 'RS TODO',

    # # Настройки сортировок

    # 1 часть - тип клиента: добивочный клиент с неактивированым черновиком, новый клиент
    # TODO:
    'activation_status_position': ...,
    # TODO:
    'unactivated_client_priority': 'UNACTIVATED_CLIENT_PRIORITY',
    # TODO:
    'new_client_priority': 'NEW_CLIENT_PRIORITY',
    # 2 часть - статус звонка, все новые задания идут с приоритетом 3 в начале, недозвоны - 2, перезвоны - 1
    # TODO:
    'call_status_position': ...,
    # TODO:
    'call_later_priority': 'CALL_LATER_PRIORITY',
    # TODO:
    'call_missed_priority': 'CALL_MISSED_PRIORITY',
    # TODO:
    'waiting_priority': 'WAITING_PRIORITY',
    # 3 часть - регион, основные регионы из ключей настройки ниже ранжируются по значениям, остальные - все вместе
    # TODO:
    'region_position': '',
    # TODO:
    'main_regions_priority': 'MAIN_REGIONS_PRIORITY',
    # 4 часть - сегмент - собственник или smb
    # TODO:
    'segment_position': ...,
    # TODO:
    'smb_priority': 'SMB_PRIORITY',
    # TODO:
    'homeowner_priority': 'HOMEOWNER_PRIORITY',
    # 5 часть - статус учетной записи - нет лк на Циан, нет активных объявлений, соблюдена пропорция заданий в админке
    # и уже активных объявлений у клиента, для smb дополнительный приоритет - активный лк
    # TODO:
    'lk_position': ...,
    # TODO:
    'no_lk_smb_priority': 'NO_LK_SMB_PRIORITY',
    # TODO:
    'no_active_smb_priority': 'NO_ACTIVE_SMB_PRIORITY',
    # TODO:
    'keep_proportion_smb_priority': 'KEEP_PROPORTION_SMB_PRIORITY',
    # TODO:
    'no_lk_homeowner_priority': 'NO_LK_HOMEOWNER_PRIORITY',
    # TODO:
    'active_lk_homeowner_priority': 'ACTIVE_LK_HOMEOWNER_PRIORITY',
    # 6-7 - части приоритета для обьявления
    # 6 часть - тип сделки - продажа, аренда
    # TODO:
    'deal_type_position': ...,
    # TODO:
    'sale_priority': 'SALE_PRIORITY',
    # TODO:
    'rent_priority': 'RENT_PRIORITY',
    # 7 часть - тип недвижимости - городская, загородная, комерческая
    # TODO:
    'offer_type_position': ...,
    # TODO:
    'flat_priority': 'FLAT_PRIORITY',
    # TODO:
    'suburban_priority': 'SUBURBAN_PRIORITY',
    # TODO:
    'commercial_priority': 'COMMERCIAL_PRIORITY',
    # 'creation_date_position': ...,
    # 'commercial_position': ...,
    # 'subsegment_position': ...,

    # # Настройки промокодов

    'promocode_polygons': 'PROMOCODE_POLYGONS',
    'regions_with_paid_publication': 'REGIONS_WITH_PAID_PUBLICATION',
    # 'filling': 'достать из RS',
    # 'promocode_price': 'достать из RS',
    'promocode_period': 'ENABLE_THIRTY_DURATION',
    'promocode_group_name': 'PROMOCODE_GROUP_NAME',
}
