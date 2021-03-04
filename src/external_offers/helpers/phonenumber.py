def transform_phone_number_to_canonical_format(num: str) -> str:
    return '+7'+num[1:] if (num.startswith('8') or num.startswith('7')) else num


def transform_phone_number_to_inner_format(num: str) -> str:
    if num.startswith('7'):
        return '8'+num[1:]
    if num.startswith('+7'):
        return '8'+num[2:]
    return num
