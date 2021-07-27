from external_offers.entities import parsed_offers
from external_offers.entities.create_test_client import CreateTestClientRequest, CreateTestClientResponse
from external_offers.entities.create_test_offer import CreateTestOfferRequest, CreateTestOfferResponse
from external_offers.repositories.postgresql.clients import save_client, get_client_by_avito_user_id
from external_offers.repositories.postgresql.parsed_offers import save_parsed_offer
from external_offers.entities.clients import Client
from external_offers.entities.parsed_offers import ParsedOffer
from external_offers.entities.offers import Offer
from external_offers.helpers.uuid import generate_guid
from external_offers.enums.client_status import ClientStatus

client_id = '59abcb4a-3c50-4391-9ceb-91dc3adcc925'
client_id = generate_guid()
# status = 'declined'
status = ClientStatus.waiting
client_phones = [88005553535]
# last_call_id = 'd091d376-6041-4681-b798-ecb6e129a241'
last_call_id = None
avito_user_id = '6960b9caba94ad3aa42a284d44d9fbfb'
is_calltracking = False
is_test = True
synced_with_kafka = False
synced_with_grafana = False


default_client = {
    'avito_user_id': avito_user_id,
    'client_phones': client_phones,
    'client_name': 'Тестовый пользак',
    'cian_user_id': '',
    'client_email': '',
    'segment': 'c',
    # 'main_account_chosen': False,
    # 'status': ClientStatus.waiting,
    # 'operator_user_id': None,
    # 'last_call_id': None,
    # 'calls_count': 0,
    # 'next_call': None,
}
parsed_offer1 = {
    'id': 'ad49365b-caa3-4d8a-be58-02360ad338d5',
    'user_segment': 'c',
    'source_object_id': '1_1308836235',
    'source_user_id': avito_user_id,
    'source_object_model': {
    'lat': '55.799034118652344',
    'lng': '37.782142639160156',
    'url': 'https://www.avito.ru/moskva/komnaty/komnata_13_m_v_3-k_35_et._1308836235',
    'town': 'Москва',
    'price': 16000,
    'title': 'Комната 13 м² в 3-к, 3/5 эт.',
    'phones': client_phones,
    'region': 1,
    'address': 'Москва, 3-я Парковая ул.',
    'contact': 'Екатерина',
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
    'is_calltracking': is_calltracking,
    'timestamp': '2021-07-26 15:40:03+03',
    'created_at': '2021-03-17 12:50:41.217007+03',
    'updated_at': '2021-07-26 13:35:54.110502+03',
    'synced': False,
    'user_synced': ''
}
offer1 = {
    'id': '38d96def-a4cc-4296-9218-b652eea10d7d',
    'parsed_id': 'ad49365b-caa3-4d8a-be58-02360ad338d5',
    'offer_cian_id': '',
    'client_id': client_id,
    'status': status,
    'created_at': '2021-03-31 02:22:48.666369+03',
    'started_at': '',
    'synced_at': '2021-03-30 15:10:20+03',
    'promocode': '',
    'priority': '',
    'last_call_id': last_call_id,
    'parsed_created_at': '2021-04-20 18:22:41.064379+03',
    'category': '',
    'synced_with_kafka': synced_with_kafka,
    'synced_with_grafana': synced_with_grafana
}
parsed_offer2 = {
    'id': 'de1b75ed-d1a1-41e6-bf8b-a20d8315e459',
    'user_segment': 'c',
    'source_object_id': '1_1787742000',
    'source_user_id': avito_user_id,
    'source_object_model': {
        'lat': '55.799034118652344',
        'lng': '37.782142639160156',
        'url': 'https://www.avito.ru/moskva/komnaty/komnata_13_m_v_2-k_45_et._1787742000',
        'town': 'Москва',
        'price': 16000,
        'title': 'Комната 13 м² в 2-к, 4/5 эт.',
        'phones': client_phones,
        'region': 1,
        'address': 'Москва, 3-я Парковая ул.',
        'contact': 'Екатерина',
        'category': 'roomRent',
        'isAgency': 1,
        'isStudio': None,
        'priceType': 6,
        'totalArea': 13,
        'livingArea': None,
        'roomsCount': 2,
        'updateDate': '2021-07-07 15:19:00',
        'description': 'Сдаётся комната на длительный срок аренды , для проживания вся мебель и техника имеется , рассмотрим всех приличных , комиссия',
        'floorNumber': 4,
        'floorsCount': 5,
        'isDeveloper': None
    },
    'is_calltracking': is_calltracking,
    'timestamp': '2021-07-26 15:38:28+03',
    'created_at': '2021-03-10 12:22:44.445029+03',
    'updated_at': '2021-07-26 12:59:09.994044+03',
    'synced': False,
    'user_synced': ''
}
offer2 = {
    'id': 'ae07a1e9-2db9-4abb-8abd-8906ff9e0b56',
    'parsed_id': 'de1b75ed-d1a1-41e6-bf8b-a20d8315e459',
    'offer_cian_id': '',
    'client_id': client_id,
    'status': status,
    'created_at': '2021-03-31 02:35:31.433442+03',
    'started_at': '',
    'synced_at': '2021-03-30 15:09:32+03',
    'promocode': '',
    'priority': '',
    'last_call_id': last_call_id,
    'parsed_created_at': '2021-04-20 18:22:41.064379+03',
    'category': '',
    'synced_with_kafka': synced_with_kafka,
    'synced_with_grafana': synced_with_grafana
}

async def create_test_client_public(request: CreateTestClientRequest, user_id: int) -> CreateTestClientResponse:
    is_test = True
    client_id = generate_guid()
    status = ClientStatus.waiting
    operator_user_id = None
    last_call_id = None
    calls_count = 0
    next_call = None
    if request.use_default:
        avito_user_id = default_client['avito_user_id']
        client_phones = default_client['client_phones']
        client_name = default_client['client_name']
        cian_user_id = default_client['cian_user_id']
        client_email = default_client['client_email']
        segment = default_client['segment']
        main_account_chosen = default_client['main_account_chosen']
    else:
        avito_user_id = request.avito_user_id
        client_phones = request.client_phones
        client_name = request.client_name
        cian_user_id = request.cian_user_id
        client_email = request.client_email
        segment = request.segment
        main_account_chosen = request.main_account_chosen
    client = Client(
        # dynamic params
        avito_user_id = avito_user_id,
        client_phones = client_phones,
        client_name = client_name,
        cian_user_id = cian_user_id,
        client_email = client_email,
        segment = segment,
        main_account_chosen = main_account_chosen,
        # static params
        is_test = is_test,
        client_id = client_id,
        status = status,
        operator_user_id = operator_user_id,
        last_call_id = last_call_id,
        calls_count = calls_count,
        next_call = next_call,
    )
    await save_client(
        client=client
    )
    return CreateTestClientResponse(
        success=True,
        message=f'Тестовый клиент был успешно создан. id: {client_id}'
    )


async def create_test_offer_public(request: CreateTestOfferRequest, user_id: int) -> CreateTestOfferResponse:
    offer_id = generate_guid()
    source_object_id = request.source_object_id
    client = await get_client_by_avito_user_id(
        avito_user_id=source_object_id,
    )

    parsed_offer_message = ParsedOfferMessage(
        id = id
        source_object_id = source_object_id
        source_object_model = source_object_model
        is_calltracking = is_calltracking
        timestamp = timestamp
        source_user_id = source_user_id
        user_segment = user_segment
    )
    parsed_offer = save_parsed_offer(parsed_offer=parsed_offer_message)
    offer = Offer(
        id='...',
        parsed_id='...',
        client_id='...',
        status='...',
        created_at='...',
        synced_at='...',
        parsed_created_at='...',
        priority='...',
        offer_cian_id='...',
        promocode='...',
        last_call_id='...',
        started_at='...',
        category='...',
        synced_with_kafka='...',
        is_test='...',
    )
    return CreateTestOfferResponse(
        success=True,
        message=f'Обьявление было успешно создано. id: {offer.id}'
    )
