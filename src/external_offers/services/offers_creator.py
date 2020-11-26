import logging
import uuid
from datetime import datetime

from cian_json import json

from external_offers.entities import Offer
from external_offers.entities.clients import Client
from external_offers.enums import ClientStatus
from external_offers.repositories.postgresql import (
    clear_waiting_offers_and_clients_with_off_limit_number_of_offers,
    get_client_by_avito_user_id,
    get_last_sync_date,
    get_offers_parsed_ids_by_parsed_ids,
    save_client,
    save_offer_for_call,
    set_synced_and_fetch_parsed_offers_chunk,
)


logger = logging.getLogger(__name__)


async def sync_offers_for_call_with_parsed():
    """ Синхронизировать таблицу заданий offers_for_call и parsed_offers """

    last_sync_date = await get_last_sync_date()
    while parsed_offers := await set_synced_and_fetch_parsed_offers_chunk(last_sync_date=last_sync_date):
        logger.info('Fetched %d parsed offers', len(parsed_offers))

        rows = await get_offers_parsed_ids_by_parsed_ids([offer.id for offer in parsed_offers])
        parsed_offer_ids_existing = set(row['parsed_id'] for row in rows)

        for parsed_offer in parsed_offers:
            if parsed_offer.id in parsed_offer_ids_existing:
                continue

            client = await get_client_by_avito_user_id(parsed_offer.source_user_id)
            if client:
                if client.status.is_declined or client.status.is_accepted:
                    continue
            else:
                client_phones = json.loads(parsed_offer.phones)
                client_contact = parsed_offer.contact

                client_id = str(uuid.uuid4())
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

    await clear_waiting_offers_and_clients_with_off_limit_number_of_offers()
