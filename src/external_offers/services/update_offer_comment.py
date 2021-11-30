from external_offers.entities.update_offer_comment import UpdateOfferCommentRequest, UpdateOfferCommentResponse
from external_offers.repositories.postgresql.offers import update_offer_comment_by_offer_id


async def update_offer_comment_public(request: UpdateOfferCommentRequest, user_id: int) -> UpdateOfferCommentResponse:
    await update_offer_comment_by_offer_id(
        offer_id=request.offer_id,
        comment=request.comment,
    )
    message = 'Коментарий к обьявлению был успешно обновлен.'
    success = True
    return UpdateOfferCommentResponse(success=success, message=message)
