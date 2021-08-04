import asyncio
from datetime import datetime
from typing import Optional

from cian_core.statsd import statsd

from my_offers import entities, pg
from my_offers.helpers.category import get_types
from my_offers.helpers.fields import get_sort_date, is_test
from my_offers.helpers.status_tab import get_status_tab
from my_offers.mappers.object_model import object_model_mapper
from my_offers.repositories import postgresql
from my_offers.repositories.monolith_cian_announcementapi.entities.object_model import ObjectModel
from my_offers.repositories.postgresql.agents import get_master_user_id
from my_offers.repositories.postgresql.billing import get_offer_publisher_user_id
from my_offers.repositories.postgresql.blocks import advisory_lock_for_offer_id
from my_offers.services import similars
from my_offers.services.announcement.fields.prices import get_prices
from my_offers.services.announcement.fields.search_text import get_search_text
from my_offers.services.announcement.fields.services import get_services
from my_offers.services.announcement.fields.street_name import get_street_name
from my_offers.services.announcement.fields.total_area import get_total_area
from my_offers.services.announcement.fields.walking_time import get_walking_time
from my_offers.services.offers import delete_offers


FAKE_ROW_VERSION = -1


async def process_announcement(object_model: ObjectModel, event_date: datetime) -> None:
    processor = MainAnnouncementProcessor(event_date)
    await processor.process(object_model)


class AnnouncementProcessor:

    async def process(self, object_model: ObjectModel):
        master_user_id = await get_master_user_id(object_model.user_id)
        payed_by = await get_offer_publisher_user_id(object_model.id)
        offer = self._prepare_offer(
            object_model=object_model,
            master_user_id=master_user_id if master_user_id else object_model.user_id,
            payed_by=payed_by
        )

        conn = pg.get()
        async with conn.transaction():
            await advisory_lock_for_offer_id(object_model.id)
            if await self._save_offer(offer):
                await self._post_process_offer(offer=offer, object_model=object_model)

    async def _save_offer(self, offer: entities.Offer) -> bool:
        raise NotImplementedError()

    def _prepare_offer(
            self,
            *,
            object_model: ObjectModel,
            master_user_id: int,
            payed_by: Optional[int]
    ) -> entities.Offer:
        """
        Метод для заполнения полей модели данными.
        Желательно оставлять синхронным и выносить всю сложную логику наверх.
        """
        offer_type, deal_type = get_types(object_model.category)
        status_tab = get_status_tab(
            offer_flags=object_model.flags,
            offer_status=object_model.status,
        )
        total_area = get_total_area(total_area=object_model.total_area, land=object_model.land)
        price, price_per_meter = get_prices(bargain_terms=object_model.bargain_terms, total_area=total_area)
        geo = object_model.geo

        offer = entities.Offer(
            offer_id=object_model.id,
            master_user_id=master_user_id,
            user_id=object_model.published_user_id,
            deal_type=deal_type,
            offer_type=offer_type,
            status_tab=status_tab,
            search_text=get_search_text(object_model),
            row_version=object_model.row_version if object_model.row_version else FAKE_ROW_VERSION,
            raw_data=object_model_mapper.map_to(object_model),
            services=get_services(object_model.publish_terms),
            is_manual=not (object_model.source and object_model.source.is_upload),
            is_in_hidden_base=bool(object_model.is_in_hidden_base),
            has_photo=bool(object_model.photos),
            payed_by=payed_by,
            is_test=is_test(object_model),
            price=price,
            price_per_meter=price_per_meter,
            total_area=total_area,
            walking_time=get_walking_time(geo),
            street_name=get_street_name(geo.address) if geo else None,
            sort_date=get_sort_date(object_model=object_model, status_tab=status_tab),
        )

        return offer

    async def _post_process_offer(self, *, offer: entities.Offer, object_model: ObjectModel) -> None:
        await self._update_offer_import_error(object_model)
        await similars.update(object_model)
        await self._add_to_delete_queue(offer)
        await self._save_stats(offer)

    async def _update_offer_import_error(self, object_model: ObjectModel) -> None:
        if not object_model.status.is_draft:
            await postgresql.delete_offer_import_error(object_model.id)

    async def _add_to_delete_queue(self, offer: entities.Offer) -> None:
        if offer.status_tab.is_deleted:
            await delete_offers([offer.offer_id])

    async def _save_stats(self, offer: entities.Offer) -> None:
        statsd.incr('offer.change.{}.{}.{}'.format(
            offer.status_tab.value,
            'manual' if offer.is_manual else 'import',
            'test' if offer.is_test else 'prod',
        ))


class MainAnnouncementProcessor(AnnouncementProcessor):

    def __init__(self, event_date: datetime) -> None:
        self._event_date = event_date

    async def _save_offer(self, offer: entities.Offer) -> bool:
        if offer.status_tab.is_archived:
            result = await postgresql.save_offer_archive(offer=offer, event_date=self._event_date)
        else:
            result = await postgresql.save_offer(offer=offer, event_date=self._event_date)

        return result


class ForceAnnouncementProcessor(AnnouncementProcessor):

    async def _save_offer(self, offer: entities.Offer) -> bool:
        await postgresql.update_offer(offer)

        return True
