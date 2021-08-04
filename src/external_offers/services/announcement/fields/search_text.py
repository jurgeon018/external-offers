import logging
import re
from typing import List, Optional, Pattern, Union

from my_offers.helpers.title import get_offer_title
from my_offers.repositories.monolith_cian_announcementapi.entities import (
    AddressInfo,
    DistrictInfo,
    HighwayInfo,
    ObjectModel,
    RailwayInfo,
    UndergroundInfo,
)


logger = logging.getLogger(__name__)


HOME_PATTERN: Pattern = re.compile(r'(([двлкс]+)([\d\/]+[^кс]?))', re.IGNORECASE)


def get_search_text(object_model: ObjectModel) -> str:
    result = [str(object_model.cian_id)]  # ID объявления

    # Номер телефона в объявлении (оригинальный): независимо от того, как ты вводишь номер телефона,
    # убираются все знаки препинания и пробелы и ищется последовательность цифр.
    for phone in object_model.phones:
        # TODO: https://jira.cian.tech/browse/CD-77625
        if phone.number:
            result.append(phone.number)
        if source_phone := phone.source_phone:
            result.append(source_phone.number)

    if geo := object_model.geo:
        if address := geo.user_input:
            result.append(address)

        result += _collect_full_names(geo.address)           # Адрес (город, улица, дом)
        result += _get_house(geo.address)                    # доп. варианты для дома
        result += _collect_names(geo.undergrounds, 'метро')  # Метро
        result += _collect_names(geo.district, 'район')      # Район
        result += _collect_names(geo.highways, 'шоссе')      # Шоссе
        result += _collect_names(geo.railways, 'станиция')   # Жд

        if geo.jk and geo.jk.name:                                     # ЖК
            result.append(geo.jk.name + ' ЖК жилой комплекс')

    # Заголовок
    # количество комнат: 1, 2, 3, 4, 5, 6+, студия, свободная планировка
    # тип: квартира, апартаменты, комната, доля, дом, часть дома, таунхаус, участок, офис и т.д.
    result.append(get_offer_title(object_model))
    if object_model.title:
        result.append(object_model.title)
    if object_model.rooms_count and object_model.rooms_count < 6:
        result += [str(object_model.rooms_count), 'комн', 'комнатная']

    # этаж раздельно
    if floor_number := object_model.floor_number:
        result.append(str(floor_number))
    if floors_count := object_model.building and object_model.building.floors_count:
        result.append(str(floors_count))

    # Текст на карточке объявления
    # Описание
    if object_model.description:
        result.append(object_model.description)

    return ' '.join(result)


def _collect_full_names(address: List[AddressInfo]):
    if not address:
        return []

    return [item.full_name for item in address if item.full_name]


def _collect_names(
        geo_items: Optional[List[Union[DistrictInfo, HighwayInfo, RailwayInfo, UndergroundInfo]]],
        name: Optional[str] = None
) -> List[str]:
    if not geo_items:
        return []

    result = [item.name for item in geo_items]
    if name:
        result.append(name)

    return result


def _get_house(address: Optional[List[AddressInfo]]) -> List[str]:
    """
    по запросу "д7" должны находить "д7"
    по запросу "7д" должны находить "д7"
    """
    result: List[str] = []
    if not address:
        return result

    for item in address:
        if item.type and item.type.is_house:
            if house := item.name:
                if not house.startswith('вл'):
                    house = 'д' + house
                if parts := re.findall(HOME_PATTERN, house):
                    for part in parts:
                        result += part
                        result.append(part[2] + part[1])
                else:
                    logger.warning('Cant parse house: %s', house)
            break

    return result
