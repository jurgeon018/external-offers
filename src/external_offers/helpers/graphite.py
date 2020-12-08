from cian_core.graphite import graphite
from cian_core.statsd import get_prefix


_METRIC_PREFIX = get_prefix()


def send_to_graphite(*, key: str, value: int, timestamp: float) -> None:
    graphite.send(
        metric='{}.stats.{}'.format(_METRIC_PREFIX, key),
        value=value,
        timestamp=timestamp,
    )
