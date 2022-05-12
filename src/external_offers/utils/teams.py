from typing import Optional, Union

from cian_core.runtime_settings import runtime_settings

from external_offers.entities.teams import Team, TeamInfo, TeamType


def get_default_team_settings() -> dict[str, Union[str, int]]:
    return {
        'maximum_active_offers_proportion': runtime_settings.get('MAXIMUM_ACTIVE_OFFERS_PROPORTION'),
        # приоритеты
        'no_lk_smb_priority': runtime_settings.get('NO_LK_SMB_PRIORITY'),
        'no_active_smb_priority': runtime_settings.get('NO_ACTIVE_SMB_PRIORITY'),
        'keep_proportion_smb_priority': runtime_settings.get('KEEP_PROPORTION_SMB_PRIORITY'),
        'active_lk_homeowner_priority': runtime_settings.get('ACTIVE_LK_HOMEOWNER_PRIORITY'),
        'no_lk_homeowner_priority': runtime_settings.get('NO_LK_HOMEOWNER_PRIORITY'),
        'unactivated_client_priority': runtime_settings.get('UNACTIVATED_CLIENT_PRIORITY'),
        'new_client_priority': runtime_settings.get('NEW_CLIENT_PRIORITY'),
        'call_missed_priority': runtime_settings.get('CALL_MISSED_PRIORITY'),
        'call_later_priority': runtime_settings.get('CALL_LATER_PRIORITY'),
        'waiting_priority': runtime_settings.get('WAITING_PRIORITY'),
        'smb_priority': runtime_settings.get('SMB_PRIORITY'),
        'homeowner_priority': runtime_settings.get('HOMEOWNER_PRIORITY'),
        'main_regions_priority': runtime_settings.get('MAIN_REGIONS_PRIORITY'),
        'sale_priority': runtime_settings.get('SALE_PRIORITY'),
        'rent_priority': runtime_settings.get('RENT_PRIORITY'),
        'flat_priority': runtime_settings.get('FLAT_PRIORITY'),
        'suburban_priority': runtime_settings.get('SUBURBAN_PRIORITY'),
        'commercial_priority': runtime_settings.get('COMMERCIAL_PRIORITY'),
        # настройки фильтрации
        'regions': runtime_settings.get('OFFER_TASK_CREATION_REGIONS'),
        'segments': runtime_settings.get('OFFER_TASK_CREATION_SEGMENTS'),
        'categories': runtime_settings.get('OFFER_TASK_CREATION_CATEGORIES'),
        'return_to_queue_days_after_hunted': runtime_settings.get('RETURN_TO_QUEUE_DAYS_AFTER_HUNTED', 2),
        'enable_only_unhunted_ct': False,
    }


def get_team_info(team: Optional[Team]) -> TeamInfo:
    if team:
        team_id = team.team_id
        team_type = team.team_type
        team_settings = team.get_settings()
        if not team_settings.get('main_regions_priority'):
            team_settings['main_regions_priority'] = get_default_team_settings()['main_regions_priority']
        # TODO: добавить динамическое поле в настройки команды
        team_settings['return_to_queue_days_after_hunted'] = get_default_team_settings()['return_to_queue_days_after_hunted']
    else:
        team_id = None
        team_type = TeamType.attractor
        team_settings = get_default_team_settings()
    return TeamInfo(
        team_id=team_id,
        team_settings=team_settings,
        team_type=team_type,
    )
