from simple_settings.utils import settings_stub

from external_offers.services.save_offer import statsd_incr_if_not_test_user


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
