from uuid import uuid4


def generate_uppercase_guid() -> str:
    return generate_guid().upper()


def generate_guid() -> str:
    return str(uuid4())
