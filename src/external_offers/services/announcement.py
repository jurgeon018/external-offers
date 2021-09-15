import logging
from typing import Optional

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
    offer_row_version = await get_offer_row_version_by_offer_cian_id(offer_cian_id)
    print('offer_row_version:', offer_row_version)
    if offer_row_version is None:
        return
    if offer_row_version is not None and offer_row_version > row_version:
        return
    status = await get_offer_publication_status_by_offer_cian_id(offer_cian_id)
    if status == Status.published.value:
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
    await set_offer_publication_status_by_offer_cian_id(
        offer_cian_id=offer_cian_id,
        publication_status=publication_status.value,
        row_version=row_version,
    )
    if publication_status == Status.draft:
        await set_client_unactivated_by_offer_cian_id(
            offer_cian_id=offer_cian_id,
        )
    elif publication_status == Status.published:
        await set_client_done_by_offer_cian_id(
            offer_cian_id=offer_cian_id,
        )
        await set_offer_done_by_offer_cian_id(
            offer_cian_id=offer_cian_id,
        )
