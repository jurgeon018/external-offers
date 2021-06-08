from datetime import datetime, timedelta
from typing import Dict

import pytz
from simple_settings import settings

from external_offers.entities import SaveOfferRequest
from external_offers.entities.save_offer import OfferType
from external_offers.repositories.monolith_cian_service.entities import PromoCodeGroupDetailModel
from external_offers.repositories.monolith_cian_service.entities.promo_code_group_detail_model import (
    PromoCodeGroupModel,
    ServicePackageStrategyModel,
)
from external_offers.repositories.monolith_cian_service.entities.promo_code_group_model import (
    Source,
    SubdivisionType,
    Type as PromoType,
)
from external_offers.repositories.monolith_cian_service.entities.service_package_strategy_item_model import (
    DurationInDays,
    ObjectTypeId,
    OperationTypes,
)
from external_offers.repositories.monolith_cian_service.entities.service_package_strategy_model import (
    ServicePackageStrategyItemModel,
    Type as StartegyType,
)


def map_save_request_to_promocode_detail_model(
    *,
    request: SaveOfferRequest,
    cian_user_id: int
) -> PromoCodeGroupDetailModel:
    now = datetime.now(tz=pytz.utc)

    return PromoCodeGroupDetailModel(
        promo_code_group_model=PromoCodeGroupModel(
            name=settings.PROMOCODE_GROUP_NAME,
            source=Source.other,
            type=PromoType.service_package,
            for_specific_user_ids=True,
            available_to=(now + timedelta(days=1)),
            subdivision_type=SubdivisionType.marketing,
            promo_codes_count=1,
            cian_user_ids=str(cian_user_id)
        ),
        service_package_strategy=ServicePackageStrategyModel(
            is_paid=False,
            auto_activate_for_manual_announcements=False,
            type=StartegyType.publication,
            items=[ServicePackageStrategyItemModel(
                operation_types=[
                    OperationTypes.sale,
                    OperationTypes.rent
                ],
                polygon_ids=settings.PROMOCODE_POLYGONS,
                duration_in_days=DurationInDays.thirty if settings.ENABLE_THIRTY_DURATION else DurationInDays.seven,
                debit_count=1,
                object_type_id=ObjectTypeId.any
            )]
        )
    )
