from datetime import datetime

from external_offers.repositories.monolith_cian_announcementapi.entities.object_model import ObjectModel
from external_offers.repositories.postgresql.offers import set_offer_publication_status_by_cian_id


async def process_announcement(object_model: ObjectModel, event_date: datetime) -> None:
    # Затащить ручку коротая будет показывать был ли использован промокод на публикацию
    
    # проверять по row_version?? что??
    row_version = object_model.row_version
    status = object_model.status
    cian_id = object_model.cian_id
    if cian_id and status:
        await set_offer_publication_status_by_cian_id(
            offer_cian_id=cian_id,
            publication_status=status,
        )
    pass
