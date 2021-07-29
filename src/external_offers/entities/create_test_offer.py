from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from external_offers.enums import UserSegment
from external_offers.enums.offer_status import OfferStatus

default_parsed_offer = {
    'id': 'ad49365b-caa3-4d8a-be58-02360ad338d5',
    'source_object_id': '1_1308836235',
    'source_user_id': '6960b9caba94ad3aa42a284d44d9fbfb',
    'is_calltracking': False,
    'user_segment': UserSegment.c,
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
        'updateDate': '2021-07-16 15:42:00',
        'description': 'Рассмотрим всех!для проживания все необходимое имеется,тихие соседи,места общего пользования в обычном состоянии,национальность не принципиальна,срочно!в стоимость все включено,фото реальны,комната с балконом,залог есть минимальный',
        'floorNumber': 3,
        'floorsCount': 5,
        'isDeveloper': None
    },
}


default_offer = {
    'offer_cian_id': None,
    # 'id': '38d96def-a4cc-4296-9218-b652eea10d7d',
    # 'parsed_id': 'ad49365b-caa3-4d8a-be58-02360ad338d5',
    # 'status': OfferStatus.waiting,
    # 'created_at': '2021-03-31 02:22:48.666369+03',
    # 'started_at': '',
    # 'synced_at': '2021-03-30 15:10:20+03',
    # 'promocode': '',
    # 'priority': '',
    # 'last_call_id': last_call_id,
    # 'parsed_created_at': '2021-04-20 18:22:41.064379+03',
    # 'category': '',
}
@dataclass
class CreateTestOfferRequest:
    # clients
    client_id: str
    """ID клиента к которому присвоится задание"""
    # parsed_offers
    parsed_id: str = default_parsed_offer['id']
    """Уникальный ключ спаршеного обьявления"""
    source_object_id: str = default_parsed_offer['source_object_id']
    """ID объявления на внешней площадке"""
    source_object_model: dict = default_parsed_offer['source_object_model']
    """Данные об объявлении"""
    is_calltracking: bool = default_parsed_offer['is_calltracking']
    """Есть ли коллтрекинг у объявления"""
    source_user_id: Optional[str] = default_parsed_offer['source_user_id']
    """ID пользователя на внешней площадке"""
    user_segment: UserSegment = default_parsed_offer['user_segment']
    """Сегмент пользователя"""
    # offers_for_call
    offer_cian_id: Optional[int] = default_offer['offer_cian_id']
    """Идентификатор объявления на Циане"""
    offer_priority: int = 1
    """Приоритет задачи"""
    category: str = default_parsed_offer['source_object_model']['category']
    """Категория обьявления"""


@dataclass
class CreateTestOfferResponse:
    success: bool
    """Статус операции"""
    message: str
    """Сообщение"""




# parsed_offer2 = {
#     'id': 'de1b75ed-d1a1-41e6-bf8b-a20d8315e459',
#     'user_segment': 'c',
#     'source_object_id': '1_1787742000',
#     'source_user_id': default_client['avito_user_id'],
#     'source_object_model': {
#         'lat': '55.799034118652344',
#         'lng': '37.782142639160156',
#         'url': 'https://www.avito.ru/moskva/komnaty/komnata_13_m_v_2-k_45_et._1787742000',
#         'town': 'Москва',
#         'price': 16000,
#         'title': 'Комната 13 м² в 2-к, 4/5 эт.',
#         'phones': client_phones,
#         'region': 1,
#         'address': 'Москва, 3-я Парковая ул.',
#         'contact': 'Екатерина',
#         'category': 'roomRent',
#         'isAgency': 1,
#         'isStudio': None,
#         'priceType': 6,
#         'totalArea': 13,
#         'livingArea': None,
#         'roomsCount': 2,
#         'updateDate': '2021-07-07 15:19:00',
#         'description': 'Сдаётся комната на длительный срок аренды , для проживания вся мебель и техника имеется , рассмотрим всех приличных , комиссия',
#         'floorNumber': 4,
#         'floorsCount': 5,
#         'isDeveloper': None
#     },
#     'is_calltracking': default_parsed_offer['is_calltracking'],
#     'timestamp': '2021-07-26 15:38:28+03',
#     'created_at': '2021-03-10 12:22:44.445029+03',
#     'updated_at': '2021-07-26 12:59:09.994044+03',
#     'synced': False,
#     'user_synced': ''
# }
# offer2 = {
#     'id': 'ae07a1e9-2db9-4abb-8abd-8906ff9e0b56',
#     'parsed_id': 'de1b75ed-d1a1-41e6-bf8b-a20d8315e459',
#     'offer_cian_id': '',
#     'client_id': client_id,
#     'status': status,
#     'created_at': '2021-03-31 02:35:31.433442+03',
#     'started_at': '',
#     'synced_at': '2021-03-30 15:09:32+03',
#     'promocode': '',
#     'priority': '',
#     'last_call_id': last_call_id,
#     'parsed_created_at': '2021-04-20 18:22:41.064379+03',
#     'category': '',
#     'synced_with_kafka': synced_with_kafka,
#     'synced_with_grafana': synced_with_grafana
# }