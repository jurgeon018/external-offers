# pylint: skip-file
"""

Code generated by cian-codegen; DO NOT EDIT.

To re-generate, run `codegen generate-client users`

cian-codegen version: 1.17.0

"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class RegisterUserByPhoneRequest:
    """Запрос регистрации пользователя по номеру телефона"""

    phone: str
    """Номер телефона"""
    first_name: Optional[str] = None
    """Имя пользователя"""
    is_professional: Optional[bool] = None
    """Профессионал ли регистрируемый пользователь"""
    last_name: Optional[str] = None
    """Фамилия пользователя"""
    sms_template: Optional[str] = None
    'Шаблон текста SMS сообщения с учетными данными.\r\nПример. "Ваш ID {0}, ваш пароль {1}"\r\n0 - id пользвоателяя\r\n1 - пароль пользователя'
