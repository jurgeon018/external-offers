# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client users`

cian-codegen version: 1.7.1

"""
from dataclasses import dataclass


@dataclass
class RegisteredUserDto:
    """Данные зергистрированного пользователя"""

    email: str
    """Email/логин пользователя"""
    id: int
    """Идентификатор пользователя"""
