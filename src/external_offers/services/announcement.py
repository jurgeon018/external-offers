import logging
from datetime import datetime
from typing import Optional

import pytz

from external_offers.repositories.monolith_cian_announcementapi.entities import SwaggerObjectModel
from external_offers.repositories.monolith_cian_announcementapi.entities.swagger_object_model import Status
from external_offers.repositories.postgresql.clients import (
    set_client_done_by_offer_cian_id,
    set_client_unactivated_by_offer_cian_id,
)
from external_offers.repositories.postgresql.offers import (
    get_offer_publication_status_by_offer_cian_id,
    get_offer_row_version_by_offer_cian_id,
    set_offer_done_by_offer_cian_id,
    set_offer_publication_status_by_offer_cian_id,
)


logger = logging.getLogger(__name__)


async def process_announcement(
    object_model: Optional[SwaggerObjectModel],
) -> None:
    if not object_model:
        return

    publication_status = object_model.status
    row_version = object_model.row_version
    offer_cian_id = object_model.cian_id
    if not row_version:
        return
    if offer_cian_id is None:
        return
    offer_row_version = await get_offer_row_version_by_offer_cian_id(offer_cian_id)
    if offer_row_version is None:
        return
    if offer_row_version is not None and offer_row_version > row_version:
        return
    status = await get_offer_publication_status_by_offer_cian_id(offer_cian_id)
    if not publication_status or status == Status.published.value:
        return
    await update_publication_status(
        publication_status=publication_status,
        row_version=row_version,
        offer_cian_id=offer_cian_id
    )


async def update_publication_status(
        *,
        publication_status: Status,
        row_version: int,
        offer_cian_id: int,
) -> None:
    now = datetime.now(pytz.utc)
    await set_offer_publication_status_by_offer_cian_id(
        offer_cian_id=offer_cian_id,
        publication_status=publication_status.value,
        row_version=row_version,
        status_changing_dt=now,
    )
    if publication_status == Status.draft:
        await set_client_unactivated_by_offer_cian_id(
            offer_cian_id=offer_cian_id,
            drafted_at=now,
        )
    elif publication_status == Status.published:
        await set_client_done_by_offer_cian_id(
            offer_cian_id=offer_cian_id,
            published_at=now,
        )
        await set_offer_done_by_offer_cian_id(
            offer_cian_id=offer_cian_id,
            published_at=now,
        )
