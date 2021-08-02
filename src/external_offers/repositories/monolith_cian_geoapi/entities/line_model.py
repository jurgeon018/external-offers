# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client monolith-cian-geoapi`

cian-codegen version: 1.16.3

"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class LineModel:
    """Модель для линии метро"""

    line_color: Optional[str] = None
    """RGB цвет линии метро"""
    line_id: Optional[int] = None
    """Идентификатор линии метро"""
    line_name: Optional[str] = None
    """Название линии метро"""
