import urllib.parse
from typing import Optional


def get_pagination_page_link(url: Optional[str], page_number: int) -> str:
    if not url or page_number < 1:
        return ''

    url_parts = list(urllib.parse.urlparse(url))
    query = dict(urllib.parse.parse_qsl(url_parts[4]))
    query.update({'page': str(page_number)})
    url_parts[4] = urllib.parse.urlencode(query)
    new_url = urllib.parse.urlunparse(url_parts)
    return new_url
