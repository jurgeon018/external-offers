from cian_enum import StrEnum


class UserSegment(StrEnum):
    """ Виды сегментов.

        Документация - https://conf.cian.tech/pages/viewpage.action?pageId=1270667362
    """

    a = 'a'
    """Крупные АН"""
    b = 'b'
    """АН"""
    c = 'c'
    """SMB"""
    d = 'd'
    """Собственник"""

    @classmethod
    def from_str(cls, value: str):
        return {
            'a': cls.a,
            'b': cls.b,
            'c': cls.c,
            'd': cls.d
        }[value]
