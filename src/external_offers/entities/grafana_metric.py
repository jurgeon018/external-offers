from dataclasses import dataclass


@dataclass
class SegmentedObject:
    segment_name: str
    """ Название сегмента """
    segment_count: int
    """ Количество обьектов в сегменте """
