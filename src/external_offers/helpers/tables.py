from enum import Enum
from typing import List, Type


def get_names(enum: Type[Enum]) -> List[str]:
    result = []
    for value in enum:
        result.append(value.value)

    return result
