from datetime import datetime

import pytz

from external_offers.helpers.graphite import send_to_graphite


def test_send_to_graphite__when_called__called_graphite_send(mocker):
    # arrange
    prefix = 'test.container'
    mocker.patch('external_offers.helpers.graphite._METRIC_PREFIX', prefix, autospec=False)
    graphite_send_mock = mocker.patch('external_offers.helpers.graphite.graphite.send')
    now = datetime.now(pytz.utc)
    value = 1
    key = 'test'
    graphite_send_mock.return_value = None

    # act
    send_to_graphite(
        key=key,
        value=value,
        timestamp=now
    )

    # assert
    graphite_send_mock.assert_called_once_with(
        metric=f'{prefix}.stats.{key}',
        value=1,
        timestamp=now
    )
