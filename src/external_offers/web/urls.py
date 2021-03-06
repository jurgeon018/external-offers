from cian_core.web import base_urls
from cian_http.file import ResponseFile
from cian_web import get_handler
from tornado.web import url

from external_offers import entities
from external_offers.entities.teams import GetTeamRequest, GetTeamResponse
from external_offers.repositories.moderation_confidence_index import entities as moderation_confidence_index_entities
from external_offers.services import admin, operators, teams
from external_offers.services.calls_history import handlers as call_history_handlers, services as call_history_services
from external_offers.services.clients import (
    update_client_additional_emails_public,
    update_client_additional_numbers_public,
    update_client_reason_of_decline_public,
)
from external_offers.services.return_client_by_phone import return_client_by_phone
from external_offers.services.save_offer import save_offer_public
from external_offers.services.test_objects import (
    create_test_client_public,
    create_test_offer_public,
    create_test_parsed_offer_public,
    delete_test_objects_public,
    update_test_objects_publication_status_public,
)
from external_offers.services.update_client_comment import update_client_comment_public
from external_offers.services.update_client_phone import update_client_phone_public
from external_offers.services.update_client_real_info import update_client_real_info_public
from external_offers.services.update_clients_operator import update_clients_operator_public
from external_offers.services.update_offer_category import update_offer_category_public
from external_offers.services.update_offer_comment import update_offer_comment_public
from external_offers.services.update_waiting_offers_priority import (
    create_test_offers_for_call,
    prioritize_waiting_offers_public,
)
from external_offers.web import handlers
from external_offers.web.handlers.base import PublicHandler


urlpatterns = base_urls.urlpatterns + [
    # admin
    url('/admin/offers-list/$', handlers.AdminOffersListPageHandler),
    url(r'/admin/offer-card/(?P<offer_id>[a-zA-Z0-9-]+)/$', handlers.AdminOffersCardPageHandler),
    url('/admin/teams/$', handlers.AdminTeamsPageHandler),
    url(r'/admin/operator-card/(?P<operator_id>[a-zA-Z0-9-]+)/$', handlers.AdminOperatorCardPageHandler),
    url(r'/admin/team-card/(?P<team_id>[a-zA-Z0-9-]+)/$', handlers.AdminTeamCardPageHandler),
    url(r'/admin/calls-history/$', call_history_handlers.AdminCallsHistoryPageHandler),

    # admin actions
    url('/api/admin/v1/update-offers-list/$', get_handler(
        service=admin.update_offers_list,
        method='POST',
        request_schema=entities.AdminUpdateOffersListRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/save-offer/$', get_handler(
        service=save_offer_public,
        method='POST',
        request_schema=entities.SaveOfferRequest,
        response_schema=entities.SaveOfferResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/return-client-by-phone/$', get_handler(
        service=return_client_by_phone,
        method='POST',
        request_schema=entities.ReturnClientByPhoneRequest,
        response_schema=entities.ReturnClientByPhoneResponse,
        base_handler_cls=PublicHandler,
    )),
    # ?????????????? ???? ????????????????
    url('/api/admin/v1/return-client-to-waiting/$', get_handler(
        service=admin.return_client_to_waiting_public,
        method='POST',
        request_schema=entities.ReturnClientToWaitingRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/decline-client/$', get_handler(
        service=admin.set_decline_status_for_client,
        method='POST',
        request_schema=entities.AdminDeclineClientRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/call-interrupted-client/$', get_handler(
        service=admin.set_call_interrupted_status_for_client,
        method='POST',
        request_schema=entities.AdminCallInterruptedClientRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/phone-unavailable-client/$', get_handler(
        service=admin.set_phone_unavailable_status_for_client,
        method='POST',
        request_schema=entities.AdminPhoneUnavailableClientRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/promo-given-client/$', get_handler(
        service=admin.set_promo_given_status_for_client,
        method='POST',
        request_schema=entities.AdminPromoGivenClientRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/delete-offer/$', get_handler(
        service=admin.delete_offer,
        method='POST',
        request_schema=entities.AdminDeleteOfferRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/already-published-offer/$', get_handler(
        service=admin.already_published_offer,
        method='POST',
        request_schema=entities.AdminAlreadyPublishedOfferRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/call-missed-client/$', get_handler(
        service=admin.set_call_missed_status_for_client,
        method='POST',
        request_schema=entities.AdminCallMissedClientRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/call-later-client/$', get_handler(
        service=admin.set_call_later_status_for_client,
        method='POST',
        request_schema=entities.AdminCallLaterClientRequest,
        response_schema=entities.AdminResponse,
        base_handler_cls=PublicHandler,
    )),
    # QA-??????????
    url('/api/admin/v1/create-test-offer/$', get_handler(
        service=create_test_offer_public,
        method='POST',
        request_schema=entities.CreateTestOfferRequest,
        response_schema=entities.CreateTestOfferResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/create-test-client/$', get_handler(
        service=create_test_client_public,
        method='POST',
        request_schema=entities.CreateTestClientRequest,
        response_schema=entities.CreateTestClientResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/delete-test-objects/$', get_handler(
        service=delete_test_objects_public,
        method='POST',
        request_schema=entities.DeleteTestObjectsRequest,
        response_schema=entities.DeleteTestObjectsResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/qa/v1/create-test-parsed-offer/$', get_handler(
        service=create_test_parsed_offer_public,
        method='POST',
        request_schema=entities.CreateTestParsedOfferRequest,
        response_schema=entities.CreateTestParsedOfferResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-test-object-publication-status/$', get_handler(
        service=update_test_objects_publication_status_public,
        method='POST',
        request_schema=entities.UpdateTestObjectsPublicationStatusRequest,
        response_schema=entities.UpdateTestObjectsPublicationStatusResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/create-test-offers-for-call/$', get_handler(
        service=create_test_offers_for_call,
        method='POST',
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    # ?????????????????? ??????????
    url('/api/admin/v1/update-client-phone/$', get_handler(
        service=update_client_phone_public,
        method='POST',
        request_schema=entities.UpdateClientPhoneRequest,
        response_schema=entities.UpdateClientPhoneResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-client-real-info/$', get_handler(
        service=update_client_real_info_public,
        method='POST',
        request_schema=entities.UpdateClientRealInfoRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-offer-category/$', get_handler(
        service=update_offer_category_public,
        method='POST',
        request_schema=entities.UpdateOfferCategoryRequest,
        response_schema=entities.UpdateOfferCategoryResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-client-comment/$', get_handler(
        service=update_client_comment_public,
        method='POST',
        request_schema=entities.UpdateClientCommentRequest,
        response_schema=entities.UpdateClientCommentResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-client-reason-of-decline/$', get_handler(
        service=update_client_reason_of_decline_public,
        method='POST',
        request_schema=entities.UpdateClientReasonOfDeclineRequest,
        response_schema=entities.UpdateClientReasonOfDeclineResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-client-additional-numbers/$', get_handler(
        service=update_client_additional_numbers_public,
        method='POST',
        request_schema=entities.UpdateClientAdditionalNumbersRequest,
        response_schema=entities.UpdateClientAdditionalNumbersResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-client-additional-emails/$', get_handler(
        service=update_client_additional_emails_public,
        method='POST',
        request_schema=entities.UpdateClientAdditionalEmailsRequest,
        response_schema=entities.UpdateClientAdditionalEmailsResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-clients-operator/$', get_handler(
        service=update_clients_operator_public,
        method='POST',
        request_schema=entities.UpdateClientsOperatorRequest,
        response_schema=entities.UpdateClientsOperatorResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-offer-comment/$', get_handler(
        service=update_offer_comment_public,
        method='POST',
        request_schema=entities.UpdateOfferCommentRequest,
        response_schema=entities.UpdateOfferCommentResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/prioritize-waiting-offers-public/$', get_handler(
        service=prioritize_waiting_offers_public,
        method='POST',
        request_schema=entities.PrioritizeWaitingOffersRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    # operators
    url('/api/admin/v1/create-operator-public/$', get_handler(
        service=operators.create_operator_public,
        method='POST',
        request_schema=entities.CreateOperatorRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-operator-public/$', get_handler(
        service=operators.update_operator_public,
        method='POST',
        request_schema=entities.UpdateOperatorRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/delete-operator-public/$', get_handler(
        service=operators.delete_operator_public,
        method='POST',
        request_schema=entities.DeleteOperatorRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-operators-public/$', get_handler(
        service=operators.update_operators_public,
        method='POST',
        request_schema=entities.UpdateOperatorsRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    # teams
    url('/api/admin/v1/get-team-public/$', get_handler(
        service=teams.get_team_public,
        method='POST',
        request_schema=GetTeamRequest,
        response_schema=GetTeamResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/get-waiting-offers-count-for-team-public/$', get_handler(
        service=teams.get_waiting_offers_count_for_team_public,
        method='POST',
        request_schema=entities.GetWaitingOffersCountForTeam,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/create-team-public/$', get_handler(
        service=teams.create_team_public,
        method='POST',
        request_schema=entities.CreateTeamRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/update-team-public/$', get_handler(
        service=teams.update_team_public,
        method='POST',
        request_schema=entities.UpdateTeamRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/delete-team-public/$', get_handler(
        service=teams.delete_team_public,
        method='POST',
        request_schema=entities.DeleteTeamRequest,
        response_schema=entities.BasicResponse,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/create-csv-report/$', get_handler(
        service=call_history_services.create_csv_report,
        method='POST',
        request_schema=moderation_confidence_index_entities.GetOperatorCallsFilter,
        response_schema=moderation_confidence_index_entities.GenerateCsvResponseModel,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/get-csv-report-status/$', get_handler(
        service=call_history_services.get_csv_report_status,
        method='POST',
        request_schema=moderation_confidence_index_entities.GetCsvReportStatusRequestModel,
        response_schema=moderation_confidence_index_entities.GetCsvReportStatusResponseModel,
        base_handler_cls=PublicHandler,
    )),
    url('/api/admin/v1/download-csv/$', get_handler(
        service=call_history_services.download_csv,
        method='POST',
        request_schema=moderation_confidence_index_entities.ApiCallComponentV1OperatorCallsDownloadCsvReportcsv,
        response_schema=ResponseFile,
        base_handler_cls=PublicHandler,
    )),
]
