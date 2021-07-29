from dataclasses import dataclass
from typing import Optional

from external_offers.enums import UserSegment
# from cian_core import runtime_settings

# default_offer = runtime_settings.DEFAULT_TEST_OFFER
default_offer = {
    # offers_for_call
    'offer_cian_id': None,
    'offer_priority': 1,
    # parsed_offers
    'id': 'ad49365b-caa3-4d8a-be58-02360ad338d5',
    'source_object_id': '1_1308836235',
    'source_user_id': '6960b9caba94ad3aa42a284d44d9fbfb',
    'is_calltracking': False,
    'user_segment': 'c',
    'source_object_model': {
        'lat': '55.799034118652344',
        'lng': '37.782142639160156',
        'url': 'https://www.avito.ru/moskva/komnaty/komnata_13_m_v_3-k_35_et._1308836235',
        'town': 'Москва',
        'price': 16000,
        'title': 'Комната 13 м² в 3-к, 3/5 эт.',
        'phones': ["88005553535"],
        'region': 1,
        'address': 'Москва, 3-я Парковая ул.',
        'contact': 'Тестовый клиент',
        'category': 'roomRent',
        'isAgency': 1,
        'isStudio': None,
        'priceType': 6,
        'totalArea': 13,
        'livingArea': None,
        'roomsCount': 3,
        'description': 'Рассмотрим всех!для проживания все необходимое имеется,тихие соседи,места общего пользования в обычном состоянии,национальность не принципиальна,срочно!в стоимость все включено,фото реальны,комната с балконом,залог есть минимальный',
        'floorNumber': 3,
        'floorsCount': 5,
        'isDeveloper': None
        # 'updateDate': '2021-07-16 15:42:00',
    },
}


@dataclass
class CreateTestOfferRequest:
    # clients
    client_id: str
    """ID клиента к которому присвоится задание"""
    # parsed_offers
    parsed_id: str = default_offer['id']
    """Уникальный ключ спаршеного обьявления"""
    source_object_id: str = default_offer['source_object_id']
    """ID объявления на внешней площадке"""
    source_object_model: dict = default_offer['source_object_model']
    """Данные об объявлении"""
    is_calltracking: bool = default_offer['is_calltracking']
    """Есть ли коллтрекинг у объявления"""
    source_user_id: Optional[str] = default_offer['source_user_id']
    """ID пользователя на внешней площадке"""
    user_segment: UserSegment = UserSegment.from_str(default_offer['user_segment'])
    """Сегмент пользователя"""
    # offers_for_call
    offer_cian_id: Optional[int] = default_offer['offer_cian_id']
    """Идентификатор объявления на Циане"""
    offer_priority: int = default_offer['offer_priority']
    """Приоритет задачи"""
    offer_category: str = default_offer['source_object_model']['category']
    """Категория обьявления"""


@dataclass
class CreateTestOfferResponse:
    success: bool
    """Статус операции"""
    message: str
    """Сообщение"""
