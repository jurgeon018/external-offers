from enum import Enum, EnumMeta
from typing import List


def get_names(enum: EnumMeta) -> List[str]:
    result = []
    for value in enum:  # type: Enum
        result.append(value.name)

    return result
