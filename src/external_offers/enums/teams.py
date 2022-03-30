from cian_enum import StrEnum


class TeamType(StrEnum):
    hunter = 'hunter'
    """Оператор который добывает реальный номер колтрекинговых клиентов, для последующего привлечения"""
    attractor = 'attractor'
    """Оператор который привлекает к предразмещению клиентов с реальными номерами"""
