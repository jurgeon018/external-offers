import pytest

from external_offers.templates.filters import seconds_to_time


@pytest.mark.parametrize('seconds,time', [
    ['1', '0:00:01'],
    [1, '0:00:01'],
    [3, '0:00:03'],
    [14, '0:00:14'],
    [3.14, '0:00:03'],
    ['3.14', '0:00:03'],
    ['не число', 'NaN'],
    ['3.14', '0:00:03'],
    [None, '0:00:00'],
    [True, 'NaN'],
    [False, 'NaN'],
    [10, '0:00:10'],
    [100, '0:01:40'],
    [1000, '0:16:40'],
    [2500, '0:41:40'],
])
def test_seconds_to_time(seconds, time):
    assert time == seconds_to_time(seconds)
