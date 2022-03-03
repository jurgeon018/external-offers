# from datetime import datetime
#
# import pytz
# from simple_settings import settings
#
# from external_offers.entities import BasicResponse
# # from external_offers.entities import UpdateClientPhoneError, UpdateClientRealPhoneRequest, UpdateClientRealPhoneResponse
# from external_offers.entities.kafka import CallsKafkaMessage
# from external_offers.entities.update_client_real_phone import UpdateClientRealPhoneRequest
# from external_offers.enums import CallStatus, UpdateClientPhoneErrorCode
# from external_offers.queue.kafka import kafka_preposition_calls_producer
# from external_offers.repositories.postgresql import get_client_by_client_id, set_phone_number_by_client_id
#
#
# async def update_client_real_phone_public(request: UpdateClientRealPhoneRequest, user_id: int) -> UpdateClientRealPhoneResponse:
#     """ Обновить реальный телефон клиента """
#     client_id = request.client_id
#     phone_number = request.phone_number
#
#     client = await get_client_by_client_id(client_id=client_id)
#     if not client:
#         return UpdateClientRealPhoneResponse(
#             success=False,
#             errors=[
#                 UpdateClientPhoneError(
#                     message='Пользователь с переданным идентификатором не найден',
#                     code=UpdateClientPhoneErrorCode.missing_client
#                 )
#             ]
#         )
#
#     await set_phone_number_by_client_id(
#         client_id=client_id,
#         phone_number=phone_number
#     )
#     now = datetime.now(pytz.utc)
#     await kafka_preposition_calls_producer(
#         message=CallsKafkaMessage(
#             manager_id=user_id,
#             source_user_id=client.avito_user_id,
#             user_id=client.cian_user_id,
#             phone=phone_number,
#             status=CallStatus.phone_changed,
#             call_id=client.last_call_id,
#             date=now,
#             source=settings.AVITO_SOURCE_NAME
#         ),
#         timeout=settings.DEFAULT_KAFKA_TIMEOUT
#     )
#     return UpdateClientRealPhoneResponse(success=True, errors=[])
