import logging
from datetime import datetime, timedelta
from typing import List

import pytz
from cian_core.context import new_operation_id
from simple_settings import settings

from external_offers.entities.parsed_offers import ParsedOffer
from external_offers.queue.producers import external_offers_deleted_producer
from external_offers.repositories.postgresql import (
    delete_outdated_parsed_offers,
    delete_waiting_offers_for_call_by_parsed_ids,
    get_latest_updated_at,
)


logger = logging.getLogger(__name__)


async def check_if_was_update() -> bool:
    """ Проверяем, было ли обновление за последние N часов """
    now = datetime.now(pytz.utc)
    latest_updated_at = await get_latest_updated_at()
    check_border = now - timedelta(hours=settings.OFFER_UPDATE_CHECK_WINDOW_IN_HOURS)

    return latest_updated_at and latest_updated_at > check_border


def get_updated_at_border() -> datetime:
    now = datetime.now(pytz.utc)
    update_border = now - timedelta(days=settings.OFFER_WITHOUT_UPDATE_MAX_AGE_IN_DAYS)
    return update_border


async def clear_outdated_offers_for_call(deleted_offers: List[ParsedOffer]) -> None:
    parsed_ids = [offer.id for offer in deleted_offers]
    if parsed_ids:
        await delete_waiting_offers_for_call_by_parsed_ids(
            parsed_ids=parsed_ids
        )


async def notify_about_deletion(deleted_offers: List[ParsedOffer]) -> None:
    for deleted_offer in deleted_offers:
        with new_operation_id():
            await external_offers_deleted_producer(
                source_object_id=deleted_offer.source_object_id
            )


async def clear_outdated_offers() -> None:
    if not settings.ENABLE_OUTDATED_OFFERS_CLEARING:
        logger.warning('Очистка устаревших объявлений отключена')
        return

    if settings.ENABLE_WAS_UPDATE_CHECK:
        was_update = await check_if_was_update()
        if not was_update:
            logger.warning('Очистка устаревших объявлений не была запущена из-за отстутствия обновлений')
            return
    else:
        logger.warning('Проверка наличия обновления отключена')

    updated_at_border = get_updated_at_border()
    deleted_offers = await delete_outdated_parsed_offers(
        updated_at_border=updated_at_border
    )

    await clear_outdated_offers_for_call(deleted_offers)
    await notify_about_deletion(deleted_offers)