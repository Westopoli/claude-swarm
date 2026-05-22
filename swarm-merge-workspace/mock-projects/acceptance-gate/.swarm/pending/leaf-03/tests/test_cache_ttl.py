from src.cache import Cache
def test_cache_ttl_none():
    c = Cache()
    c.set("key", "val", ttl=None)
    assert c.get("key") == "val"
def test_cache_ttl_set():
    c = Cache()
    c.set("key", "val", ttl=100)
    assert c.get("key") == "val"
