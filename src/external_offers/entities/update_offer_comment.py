from dataclasses import dataclass


@dataclass
class UpdateOfferCommentRequest:
    offer_id: str
    comment: str


@dataclass
class UpdateOfferCommentResponse:
    success: bool
    message: str
