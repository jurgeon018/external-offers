import struct
from functools import lru_cache
from pathlib import Path
from typing import IO, Optional


REALTY_ID_THRESHOLD = 12001679
CIAN_ID_THRESHOLD = 12125854
REALTY_ID_TO_CIAN_ID_FILE = (Path(__file__).parent / 'data' / 'realty_to_cian.bin').open('rb')
CIAN_ID_TO_REALTY_ID_FILE = (Path(__file__).parent / 'data' / 'cian_to_realty.bin').open('rb')


@lru_cache(maxsize=1)
def get_user_cian_id_by_realty_id(realty_id: int) -> Optional[int]:
    return _get_user_id(
        user_id=realty_id,
        file=REALTY_ID_TO_CIAN_ID_FILE,
        threshold=REALTY_ID_THRESHOLD,
    )


@lru_cache(maxsize=1)
def get_realty_id_by_cian_id(cian_id: int) -> Optional[int]:
    return _get_user_id(
        user_id=cian_id,
        file=CIAN_ID_TO_REALTY_ID_FILE,
        threshold=CIAN_ID_THRESHOLD,
    )


def _get_user_id(*, user_id: int, file: IO[bytes], threshold: int) -> Optional[int]:
    if user_id < 1:
        return None
    if user_id >= threshold:
        return user_id
    struct_size = 4
    file.seek(user_id * struct_size)
    binary_id = file.read(struct_size)

    return struct.unpack('i', binary_id)[0] or user_id
