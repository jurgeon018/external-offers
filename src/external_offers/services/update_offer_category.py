
from external_offers.entities import UpdateOfferCategoryRequest, UpdateOfferCategoryResponse
from external_offers.repositories.postgresql import update_offer_categories_by_offer_id
from external_offers.services.save_offer import mapping_offer_params_to_category


async def update_offer_category_public(request: UpdateOfferCategoryRequest, user_id: int) -> UpdateOfferCategoryResponse:
    '''Обновить категорию обьявления'''
    offer_id = request.offer_id
    try:
        category = mapping_offer_params_to_category[(
            request.term_type,
            request.category_type,
            request.deal_type,
            request.offer_type
        )]
    except KeyError as e:
        message = f"Неверная комбинация параметров: {e}."
        message += f'\nВозможнные комбинации:'
        for param in mapping_offer_params_to_category.keys():
            message += f'\n{param};'
        return UpdateOfferCategoryResponse(
            success=False,
            message=message
        )
    try:
        await update_offer_categories_by_offer_id(
            offer_id=offer_id,
            category=category,
        )
        return UpdateOfferCategoryResponse(
            success=True,
            message=f"Категория была изменена на {category.value}. Перезагрузите страницу чтобы увидеть изменения.",
        )
    except Exception as e:
        return UpdateOfferCategoryResponse(
            success=False,
            message=f"Ошибка при обновлении категории обьявления: {e}",
        )
