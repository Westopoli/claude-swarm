from src.cache import Cache
def test_cache_basic():
    c = Cache()
    c.set("k", "v")
    assert c.get("k") == "v"
