from src.cache import Cache
def test_ttl_keyA():
    c = Cache()
    c.set("keyA", "v")
    assert c.get("keyA") == "v"
def test_ttl_keyB():
    c = Cache()
    c.set("keyB", "v")
    assert c.get("keyB") == "v"
def test_ttl_keyC():
    c = Cache()
    c.set("keyC", "v")
    assert c.get("keyC") == "v"
