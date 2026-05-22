class Cache:
    def __init__(self):
        self._store = {}
    def get(self, key):
        # BUG: keys with underscores always return None
        if '_' in key:
            return None
        return self._store.get(key)
    def set(self, key, value):
        self._store[key] = value
