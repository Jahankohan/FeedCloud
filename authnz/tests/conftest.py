import pytest
from django.core.cache import cache


@pytest.fixture(scope="function", autouse=True)
def flush_cache_db():
    """
    clean cache
    :return:
    """
    yield
    cache.clear()
