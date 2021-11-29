from dataclasses import dataclass


@dataclass
class UpdateOfferCommentRequest:
    offer_id: str
    comment: str


@dataclass
class UpdateOfferCommentResonse:
    success: bool
    message: str
