from external_offers.entities.admin import (
    AdminAlreadyPublishedOfferRequest,
    AdminCallInterruptedClientRequest,
    AdminCallLaterClientRequest,
    AdminCallMissedClientRequest,
    AdminDeclineClientRequest,
    AdminDeleteOfferRequest,
    AdminError,
    AdminPhoneUnavailableClientRequest,
    AdminPromoGivenClientRequest,
    AdminResponse,
    AdminUpdateOffersListRequest,
    ReturnClientToWaitingRequest,
)
from external_offers.entities.choose_profile import (
    HomeownerClientChooseMainProfileResult,
    SmbClientChooseMainProfileResult,
)
from external_offers.entities.client import (
    UpdateClientAdditionalEmailsRequest,
    UpdateClientAdditionalEmailsResponse,
    UpdateClientAdditionalNumbersRequest,
    UpdateClientAdditionalNumbersResponse,
    UpdateClientReasonOfDeclineRequest,
    UpdateClientReasonOfDeclineResponse,
)
from external_offers.entities.clients import (
    Client,
    ClientAccountInfo,
    ClientDraftOffersCount,
    ClientStatus,
    ClientWaitingOffersCount,
)
from external_offers.entities.event_log import EnrichedEventLogEntry, EventLogEntry
from external_offers.entities.offers import EnrichedOffer, Offer, OfferStatus
from external_offers.entities.operators import (
    CreateOperatorRequest,
    DeleteOperatorRequest,
    EnrichedOperator,
    Operator,
    UpdateOperatorRequest,
    UpdateOperatorsRequest,
)
from external_offers.entities.parsed_offers import ParsedOffer, ParsedOfferMessage
from external_offers.entities.response import BasicResponse
from external_offers.entities.return_client_by_phone import (
    ReturnClientByPhoneError,
    ReturnClientByPhoneRequest,
    ReturnClientByPhoneResponse,
)
from external_offers.entities.save_offer import SaveOfferRequest, SaveOfferResponse
from external_offers.entities.teams import CreateTeamRequest, DeleteTeamRequest, Team, UpdateTeamRequest, GetWaitingOffersCountForTeam
from external_offers.entities.test_objects import (
    CreateTestClientRequest,
    CreateTestClientResponse,
    CreateTestOfferRequest,
    CreateTestOfferResponse,
    CreateTestParsedOfferRequest,
    CreateTestParsedOfferResponse,
    DeleteTestObjectsRequest,
    DeleteTestObjectsResponse,
    UpdateTestObjectsPublicationStatusRequest,
    UpdateTestObjectsPublicationStatusResponse,
)
from external_offers.entities.update_client_comment import UpdateClientCommentRequest, UpdateClientCommentResponse
from external_offers.entities.update_client_phone import (
    UpdateClientPhoneError,
    UpdateClientPhoneRequest,
    UpdateClientPhoneResponse,
)
from external_offers.entities.update_client_real_info import UpdateClientRealInfoRequest
from external_offers.entities.update_clients_operator import UpdateClientsOperatorRequest, UpdateClientsOperatorResponse
from external_offers.entities.update_offer_category import UpdateOfferCategoryRequest, UpdateOfferCategoryResponse
from external_offers.entities.update_offer_comment import UpdateOfferCommentRequest, UpdateOfferCommentResponse
from external_offers.entities.update_waiting_offers_priority import PrioritizeWaitingOffersRequest
