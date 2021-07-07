import logging

from cian_http.exceptions import ApiClientException

from external_offers.repositories.sms import v2_send_sms
from external_offers.repositories.sms.entities.send_sms_request_v2 import MessageType, SendSmsRequestV2


logger = logging.getLogger(__name__)


async def send_sms(
    *,
    message_type: MessageType,
    text: str,
    phone_number: str,
) -> None:
    try:
        await v2_send_sms(
            SendSmsRequestV2(
                message_type=message_type,
                phone=phone_number,
                text=text,
            )
        )
    except ApiClientException as exc:
        logger.warning(
            'Ошибка при отправке инструкции по смс на номер %s: %s',
            phone_number,
            exc.message
        )
