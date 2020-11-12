def transform_phone_number_to_canonical_format(num: str):
    return '+7'+num[1:] if (num.startswith('8') or num.startswith('7')) else num
