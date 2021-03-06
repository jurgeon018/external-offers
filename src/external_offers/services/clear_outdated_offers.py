import logging
from datetime import datetime, timedelta
from typing import List

import pytz
from simple_settings import settings

from external_offers.entities.parsed_offers import ParsedOffer
from external_offers.repositories.postgresql import (
    delete_outdated_parsed_offers,
    delete_waiting_offers_for_call_without_parsed_offers,
    get_latest_updated_at,
)
from external_offers.services.send_deleted_offers_to_kafka import send_deleted_offers_to_kafka


logger = logging.getLogger(__name__)


async def check_if_was_update() -> bool:
    """ Проверяем, было ли обновление за последние N часов """
    now = datetime.now(pytz.utc)
    latest_updated_at = await get_latest_updated_at()
    check_border = now - timedelta(hours=settings.OFFER_UPDATE_CHECK_WINDOW_IN_HOURS)

    return bool(latest_updated_at and latest_updated_at > check_border)


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

    await delete_outdated_parsed_offers()
    source_object_ids = await delete_waiting_offers_for_call_without_parsed_offers()
    await send_deleted_offers_to_kafka(source_object_ids)
