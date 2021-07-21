from cian_enum import NoFormat, StrEnum


class GrafanaMetric(StrEnum):
    __value_format__ = NoFormat
    waiting_offers_count = "waiting_offers.count"
    """количество заданий в ожидании в начале дня, которые будут отправлены в графану"""

    waiting_clients_count = "waiting_clients.count"
    """количество заданий в ожидании в начале дня, которые будут отправлены в графану"""

    processed_offers_count = "processed_offers.count"
    """количество обработаных заданий в конце дня. обработаные - те, которые утром попали в графану в ожидании, и в течении дня их статус поменялся """

    processed_clients_count = "processed_clients.count"
    """количество обработаных клиентов в конце дня. обработаные - те, которые утром попали в графану в ожидании, и в течении дня их статус поменялся """
    
    processed_clients_percentage = "processed_clients.percentage"
    """соотношение обработаных заданий в конце дня к утренним необработаным заданиям"""
    
    processed_offers_percentage = "processed_offers.percentage"
    """соотношение обработаных клиентов в конце дня к утренним необработаным клиентам"""


class GrafanaSegmentType(StrEnum):
    __value_format__ = NoFormat
    region = "region"
    """Регионы"""
    user_segment = "user_segment"
    """Сегменты"""
    category = "category"
    """Категории"""
