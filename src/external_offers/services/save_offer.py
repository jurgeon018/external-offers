from external_offers.entities.save_offer import SaveOfferRequest, SaveOfferResponse
from external_offers.enums.save_offer_status import SaveOfferStatus


async def save_offer_public(request: SaveOfferRequest, *, user_id: int) -> SaveOfferResponse:
    """ Сохранить объявление как черновик в ЦИАН. """

    return SaveOfferResponse(status=SaveOfferStatus.ok)
