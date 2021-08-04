from cian_enum import NoFormat, StrEnum


class AnnouncementReportingV1RoutingKey(StrEnum):
    __value_format__ = NoFormat

    published = 'published'
    """Опубликован"""
    change = 'change'
    """Изменён"""
    blocked = 'blocked'
    """Заблокирован"""
    deactivated = 'deactivated'
    """Деактивирован"""
    draft = 'draft'
    """Черновик"""
    refused_by_moderator = 'refusedbymoderator'
    """Отклонен модератором"""
    removed_by_moderator = 'removedbymoderator'
    """Удален модератором"""
    deleted = 'deleted'
    """Удален"""
    move_to_archive = 'movetoarchive'
    """В архиве"""
    delete_permanently = 'deletepermanently'
    """Удален на всегда"""

    image_changed = 'imagechanged'
    """Изменено изображение"""
    billed_after_published = 'billedafterpublished'
    """Тарификация после публикации"""
    accept_by_moderator = 'acceptbymoderator'
    """Проверка модератором объявления и его публикация"""

    removed_from_archive = 'removed_from_archive'
    # """Удалено из архива"""
    actualize_trust = 'actualizetrust'
    # """Пересчет уровня доверия"""
    change_trust_for_builder = 'changetrustforbuilder'
    # """Изменение Trust на тарифе застройщик"""
    prolong = 'prolong'
    # """Продление"""
    sold = 'sold'
    # """Продан"""
