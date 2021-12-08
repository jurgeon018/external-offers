from typing import List, Optional

from cian_core.runtime_settings import runtime_settings


_ZERO = '0'
_EMPTY = ''
_PRIORITY_LENGTH = 6
_REGION_PRIORITY_OFFSET = 100
_SECONDARY_REGION_PRIORITY = 100


def build_priority_from_blocks(
    *,
    call_status_priority: int,
    region_priority: Optional[int] = None,
    client_type_priority: Optional[int] = None,
    account_priority: Optional[int] = None
) -> int:
    """ Составляем финальный приоритет из 4 частей, добиваем до общей длины нулями и приводим к int """
    builded_priority = (
        str(call_status_priority)
        + str(client_type_priority if client_type_priority else _EMPTY)
        + str(region_priority if region_priority else _EMPTY)
        + str(account_priority if account_priority else _EMPTY)
    ).ljust(_PRIORITY_LENGTH, _ZERO)
    return int(builded_priority)


def build_region_priority_from_region(
    *,
    regions: List[int],
    team_settings: dict,
) -> int:
    """
    Ищем самый приоритетный из регионов. Для основных  - разделение по приоритетам, неосновные - все 1 приоритетом.
    Затем отступом в 100 доводим до 3-значного числа для соблюдения длины финального приоритета для всех регионов
    """
    regions_priorities = [
        team_settings['main_regions_priority'].get(
            str(region),
            _SECONDARY_REGION_PRIORITY
        )
        for region in regions
    ]
    region_priority = min(regions_priorities)

    region_priority_with_offset = region_priority + _REGION_PRIORITY_OFFSET
    return region_priority_with_offset


def build_waiting_homeowner_priority(
    *,
    regions: List[int],
    account_priority: int,
    team_settings: dict,
) -> int:
    return build_priority_from_blocks(
        call_status_priority=team_settings['waiting_priority'],
        region_priority=build_region_priority_from_region(
            regions=regions,
            team_settings=team_settings,
        ),
        client_type_priority=team_settings['homeowner_priority'],
        account_priority=account_priority
    )


def build_waiting_smb_priority(
    *,
    regions: List[int],
    account_priority: int,
    team_settings: dict,
) -> int:
    return build_priority_from_blocks(
        call_status_priority=team_settings['waiting_priority'],
        client_type_priority=team_settings['smb_priority'],
        region_priority=build_region_priority_from_region(
            regions=regions,
            team_settings=team_settings,
        ),
        account_priority=account_priority
    )


def build_call_later_priority(
    team_settings: dict,
) -> int:
    """ Не ранжируем недозвоны по регионам, сегментами и аккаунтам, их мало """
    return build_priority_from_blocks(
        call_status_priority=team_settings['call_later_priority'],
    )


def build_call_missed_priority(
    team_settings: dict,
) -> int:
    """ Не ранжируем недозвоны по регионам, сегментами и аккаунтам, их мало """
    return build_priority_from_blocks(
        call_status_priority=team_settings['call_missed_priority'],
    )
