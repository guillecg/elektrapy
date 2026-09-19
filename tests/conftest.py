import pytest


@pytest.fixture(scope="session", autouse=True)
def data_dir() -> str:
    yield "tests/data/"
