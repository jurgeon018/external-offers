from cian_http.exceptions import ApiClientException
from cian_test_utils import future
from simple_settings.utils import settings_stub

from external_offers.repositories.sms.entities.send_sms_request_v2 import MessageType
from external_offers.services.save_offer import send_instruction, statsd_incr_if_not_test_user
from external_offers.services.sms import send_sms


SMB_WELCOME_INSTRUCTION: str = """
Ваше объявление ожидает бесплатной публикации на Циан:
1)Зайдите в кабинет my.cian.ru в раздел «Мои объявления.beta», вкладка «Неактивные»
2)Отредактируйте объект: проверьте данные, загрузите фото
3)Выберите тариф за 0₽
4)Сохраните изменения
Готово!
"""

HOMEOWNER_WELCOME_INSTRUCTION: str = """
Ваше объявление ожидает бесплатной публикации на Циан:
1)Зайдите на my.cian.ru в раздел «Сводка», восстановите объявление с отметкой «В архиве»
3)Отредактируйте объект: проверьте данные, загрузите фото
4)Выберите тариф за 0₽
5)Сохраните
Готово!
"""


def test_save_offer__not_test_operator_user_id__statsd_incr_not_called(mocker):
    metric = 'test_metric'
    user_id = 1

    statsd_incr_mock = mocker.patch('external_offers.services.save_offer.statsd.incr')
    with settings_stub(TEST_OPERATOR_IDS=[2]):
        statsd_incr_if_not_test_user(
            metric=metric,
            user_id=user_id
        )

    assert statsd_incr_mock.called

def test_save_offer__test_operator_user_id__statsd_incr_not_called(mocker):
    metric = 'test_metric'
    user_id = 1

    statsd_incr_mock = mocker.patch('external_offers.services.save_offer.statsd.incr')
    with settings_stub(TEST_OPERATOR_IDS=[1]):
        statsd_incr_if_not_test_user(
            metric=metric,
            user_id=user_id
        )

    assert not statsd_incr_mock.called


async def test_save_offer__is_by_home_owner__homeowner_instruction_is_sent(
    mocker,
    fake_settings,
):
    await fake_settings.set(
        HOMEOWNER_WELCOME_INSTRUCTION=HOMEOWNER_WELCOME_INSTRUCTION
    )
    send_sms_mock = mocker.patch(
        'external_offers.services.save_offer.send_sms',
        return_value=future(),
    )
    phone_number = '123'
    await send_instruction(
        is_by_home_owner=True,
        phone_number=phone_number,
    )
    send_sms_mock.assert_called_once_with(
        message_type=MessageType.b2b_homeowner_welcome_instruction,
        text=HOMEOWNER_WELCOME_INSTRUCTION,
        phone_number=phone_number,
    )


async def test_save_offer__is_not_by_home_owner__smb_instruction_is_sent(
    mocker,
    fake_settings,
):
    await fake_settings.set(
        SMB_WELCOME_INSTRUCTION=SMB_WELCOME_INSTRUCTION
    )
    send_sms_mock = mocker.patch(
        'external_offers.services.save_offer.send_sms',
        return_value=future()
    )
    phone_number = '123'
    await send_instruction(
        is_by_home_owner=False,
        phone_number=phone_number,
    )
    send_sms_mock.assert_called_once_with(
        message_type=MessageType.b2b_smb_welcome_instruction,
        text=SMB_WELCOME_INSTRUCTION,
        phone_number=phone_number,
    )


async def test_save_offer__is_not_by_home_owner__sms_is_not_sent(mocker):
    mocker.patch(
        'external_offers.services.sms.v2_send_sms',
        side_effect=ApiClientException('error')
    )
    logger_warning_mock = mocker.patch('external_offers.services.sms.logger.warning')
    await send_sms(
        message_type=MessageType.b2b_smb_welcome_instruction,
        text='text',
        phone_number='+33333333',
    )
    assert logger_warning_mock.called is True
