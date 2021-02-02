import freezegun
import pytest
import pytz
from cian_test_utils import future
from freezegun.api import FakeDatetime

from external_offers.services.send_latest_timestamp_to_graphite import send_parsed_offers_timestamp_diff_to_graphite


@pytest.mark.gen_test
@freezegun.freeze_time('2020-12-10 09:57:30.303690+00:00')
async def test_send_parsed_offers_timestamp_diff_to_graphite__when_called__send_to_graphite_called(mocker):
    # arrange
    get_timestamp_mock = mocker.patch('external_offers.services.send_latest_timestamp_'
                                      'to_graphite.get_lastest_event_timestamp')
    send_to_graphite_mock = mocker.patch('external_offers.services.send_latest_timestamp_to_graphite.send_to_graphite')
    last_timestamp = FakeDatetime(2020, 10, 10, 9, 57, 30, 303690, tzinfo=pytz.UTC)
    freezed_now = FakeDatetime.now(pytz.UTC)
    get_timestamp_mock.return_value = future(last_timestamp)
    send_to_graphite_mock.return_value = None

    # act
    await send_parsed_offers_timestamp_diff_to_graphite()

    # assert
    assert get_timestamp_mock.called
    send_to_graphite_mock.assert_called_once_with(
        key='parsed_offers.seconds_since_last_timestamp',
        value=(freezed_now - last_timestamp).total_seconds(),
        timestamp=freezed_now.timestamp()
    )
