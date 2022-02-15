from external_offers.repositories.postgresql.operators import get_operators_by_team_id
from external_offers.services.calls_history.helpers import get_pagination_page_link
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
        if current_operator.team_id:
            operators = await get_operators_by_team_id(current_operator.team_id)
        else:
            operators = [current_operator]
        search = CallsHistorySearch.from_search_params(self._get_search_params(), self.realty_user_id)
        calls = await search.execute()
        previous_page_link = get_pagination_page_link(self.request.uri, search.page - 1) if self.request.uri else ''
        next_page_link = get_pagination_page_link(self.request.uri, search.page + 1) if self.request.uri else ''
        self.write(get_html(
            'operator_calls_history.jinja2',
            current_operator=current_operator,
            operators=operators,
            calls=calls,
            selected_operator_id=search.operator_id,
            filter_data=calls_history_mapper.map_to(search),
            previous_page_link=previous_page_link,
            next_page_link=next_page_link,
        ))
