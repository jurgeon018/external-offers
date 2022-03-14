import math
import urllib.parse
from dataclasses import dataclass


@dataclass
class PageItem:
    link: str
    """Ссылка на страницу"""
    text: str
    """Текст кнопки"""
    is_active: bool = False
    """Активна ли сейчас"""


@dataclass
class Paginator:
    url: str
    """URL запроса"""
    current_page_number: int
    """Текущая страница"""
    total_count: int
    """Всего элементов (не страниц)"""
    page_size: int
    """Элементов на странице"""

    @staticmethod
    def get_page_link(url: str, page_number: int) -> str:
        url_parts = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update({'page': str(page_number)})
        url_parts[4] = urllib.parse.urlencode(query)
        new_url = urllib.parse.urlunparse(url_parts)
        return new_url

    @property
    def page_count(self):
        return int(math.ceil(self.total_count / self.page_size))

    def get_page_items(self) -> list[PageItem]:
        if self.page_count <= 1:
            return []

        previous_page = self.current_page_number - 1 if self.current_page_number > 1 else None
        next_page = self.current_page_number + 1 if self.current_page_number < self.page_count else None

        result = []
        if previous_page:
            link = self.get_page_link(self.url, previous_page)
            result.append(PageItem(link=link, text='Предыдущая'))
        for page_num in range(1, self.page_count + 1):
            link = self.get_page_link(self.url, page_num)
            is_active = (self.current_page_number == page_num)
            result.append(PageItem(link=link, text=str(page_num), is_active=is_active))
        if next_page:
            link = self.get_page_link(self.url, next_page)
            result.append(PageItem(link=link, text='Следующая'))
        return result
