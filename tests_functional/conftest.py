import pytest


@pytest.fixture(autouse=True, scope='session')
async def start():
    pass
