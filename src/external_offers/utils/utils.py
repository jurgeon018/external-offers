from typing import Generator, Iterable, TypeVar

from simple_settings import settings


T = TypeVar('T')


def iterate_over_list_by_chunks(
    *,
    iterable: Iterable[T],
    chunk_size: int = settings.ITERATE_OVER_LIST_DEFAULT_CHUNK
) -> Generator[Iterable[T], None, None]:
    iterator = iter(iterable)
    while True:
        chunk = []
        try:
            for _ in range(chunk_size):
                chunk.append(next(iterator))
            yield chunk
        except StopIteration:
            if chunk:
                yield chunk
            break
