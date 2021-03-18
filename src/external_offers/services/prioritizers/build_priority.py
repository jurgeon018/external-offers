from typing import List, Optional

from simple_settings import settings


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
    builded_priority = (
        str(call_status_priority)
        + str(region_priority if region_priority else _EMPTY)
        + str(client_type_priority if client_type_priority else _EMPTY)
        + str(account_priority if account_priority else _EMPTY)
    ).ljust(_PRIORITY_LENGTH, _ZERO)

    return int(builded_priority)


def build_region_priority_from_region(
    *,
    regions: List[int]
) -> int:
    try:
        regions_priorities = [settings.MAIN_REGIONS_PRIORITY.index(region) for region in regions]
        region_priority = min(regions_priorities)
    except ValueError:
        region_priority = _SECONDARY_REGION_PRIORITY

    region_priority_with_offset = region_priority + _REGION_PRIORITY_OFFSET
    return region_priority_with_offset


def build_waiting_homeowner_priority(
    *,
    regions: List[int],
    account_priority: int
) -> int:
    return build_priority_from_blocks(
        call_status_priority=settings.WAITING_PRIORITY_BLOCK,
        region_priority=build_region_priority_from_region(
            regions=regions
        ),
        client_type_priority=settings.HOMEOWNER_PRIORITY,
        account_priority=account_priority
    )


def build_waiting_smb_priority(
    *,
    regions: List[int],
    account_priority: int
) -> int:
    return build_priority_from_blocks(
        call_status_priority=settings.WAITING_PRIORITY_BLOCK,
        client_type_priority=settings.SMB_PRIORITY,
        region_priority=build_region_priority_from_region(
            regions=regions
        ),
        account_priority=account_priority
    )


def build_call_later_priority() -> int:
    return build_priority_from_blocks(
        call_status_priority=settings.CALL_LATER_PRIORITY_BLOCK
    )


def build_call_missed_priority() -> int:
    return build_priority_from_blocks(
        call_status_priority=settings.CALL_MISSED_PRIORITY_BLOCK
    )
