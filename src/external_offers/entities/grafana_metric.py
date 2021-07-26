from dataclasses import dataclass

from external_offers.enums.grafana_metric import GrafanaSegmentType


@dataclass
class SegmentedObject:
    segment_name: GrafanaSegmentType
    """ Название сегмента """
    segment_count: int
    """ Количество обьектов в сегменте """
