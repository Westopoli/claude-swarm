from src.cache import Cache
def test_cache_miss_returns_none():
    c = Cache()
    assert c.get("missing") is None
