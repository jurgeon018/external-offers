import logging
import uuid
from datetime import datetime

from cian_json import json

from external_offers.entities import Offer
from external_offers.entities.clients import Client
from external_offers.enums import ClientStatus
from external_offers.repositories.postgresql import (
    get_client_by_avito_user_id,
    get_last_sync_date,
    get_offers_by_parsed_id,
    save_client,
    save_offer_for_call,
    set_synced_and_fetch_parsed_offers_chunk,
)


logger = logging.getLogger(__name__)


async def create_offers_for_call_from_parsed():
    """ Создать задания из таблицы `parsed_offers` """

    last_sync_date = await get_last_sync_date()

    while parsed_offers := await set_synced_and_fetch_parsed_offers_chunk(last_sync_date=last_sync_date):
        logger.info('Fetched %d parsed offers', len(parsed_offers))

        for parsed_offer in parsed_offers:
            existing_offer = await get_offers_by_parsed_id(parsed_offer.id)

            if existing_offer:
                continue

            client = await get_client_by_avito_user_id(parsed_offer.source_user_id)
            if client:
                if client.status.is_declined:
                    continue
            else:
                source_object_model = json.loads(parsed_offer.source_object_model)
                client_id = str(uuid.uuid4())
                client_phones = source_object_model.get('phones')
                client_contact = source_object_model.get('contact')
                client = Client(
                    client_id=client_id,
                    avito_user_id=parsed_offer.source_user_id,
                    client_name=client_contact,
                    client_phones=client_phones if client_phones else [],
                    status=ClientStatus.waiting
                )
                await save_client(client)

            offer_id = str(uuid.uuid4())
            now = datetime.now()
            offer = Offer(
                id=offer_id,
                parsed_id=parsed_offer.id,
                client_id=client.client_id,
                status=client.status,
                created_at=now,
                synced_at=parsed_offer.timestamp
            )

            await save_offer_for_call(offer=offer)
