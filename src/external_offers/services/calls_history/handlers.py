from external_offers.repositories.postgresql.clients import (
    get_hunted_numbers_by_operator_id,
    get_hunted_numbers_for_date_by_operator_id,
)
from external_offers.repositories.postgresql.operators import get_enriched_operators
from external_offers.services.calls_history.helpers import Paginator
from external_offers.services.calls_history.mappers import calls_history_mapper
from external_offers.services.calls_history.search import CallsHistorySearch
from external_offers.services.operator_roles import get_or_create_operator
from external_offers.templates import get_html
from external_offers.web.handlers.base import PublicHandler


class AdminCallsHistoryPageHandler(PublicHandler):
    # pylint: disable=abstract-method

    def _get_search_params(self) -> dict:
        data = {k: self.get_argument(k) for k in self.request.arguments}
        return data

    async def get(self) -> None:
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        current_operator = await get_or_create_operator(
            operator_id=self.realty_user_id,
        )
        operators = await get_enriched_operators()
        search = CallsHistorySearch.from_search_params(self._get_search_params(), self.realty_user_id)
        calls_response = await search.execute()
        total_calls_count = calls_response.total or 0
        paginator = Paginator(
            url=self.request.uri or '',
            current_page_number=search.page,
            total_count=total_calls_count,
            page_size=search.page_size,
        )
        selected_operator_id = search.operator_id
        hunted_numbers_for_today = await get_hunted_numbers_for_date_by_operator_id(
            hunter_user_id=selected_operator_id,
            dt_lower_border=search.dt_lower_border,
            dt_upper_border=search.dt_upper_border,
        )
        all_hunted_numbers = await get_hunted_numbers_by_operator_id(
            hunter_user_id=selected_operator_id
        )
        self.write(get_html(
            'operator_calls_history.jinja2',
            current_operator=current_operator,
            operators=operators,
            calls=calls_response.calls,
            selected_operator_id=selected_operator_id,
            hunted_numbers_for_today=hunted_numbers_for_today,
            all_hunted_numbers=all_hunted_numbers,
            filter_data=calls_history_mapper.map_to(search),
            paginator=paginator.get_page_items(),
            total_calls_count=total_calls_count,
        ))
